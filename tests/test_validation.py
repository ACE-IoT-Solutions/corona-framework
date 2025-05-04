import pytest
from rdflib import Graph, Literal, URIRef # Added Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from pyshacl import validate
import os
import sys

# Ensure src directory is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__)) # tests directory
project_root = os.path.dirname(script_dir) # project root (corona-standard)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import necessary components from the project
from models import BaseMetric, CORONA, BACNET, format_rdflib_literal, to_camel_case
from demo_metrics import generate_all_sample_metrics


# --- Helper function (similar to main.py) ---
def add_metric_to_graph(metric: BaseMetric, g: Graph):
    """Adds the triples for a single metric instance to an existing RDFLib Graph."""
    try:
        instance_uri = URIRef(metric.metric_instance_uri)
    except Exception as e:
        pytest.fail(f"Invalid metric_instance_uri '{metric.metric_instance_uri}': {e}")
        return

    g.add((instance_uri, RDF.type, CORONA[metric.__class__.__name__]))

    if metric.observed_from:
        observed_from_term = format_rdflib_literal(metric.observed_from)
        g.add((instance_uri, CORONA.observedFrom, observed_from_term))
    if metric.description:
        g.add((instance_uri, RDFS.comment, Literal(metric.description)))
    if metric.metric_identifier:
        g.add((instance_uri, CORONA['metric-identifier'], Literal(metric.metric_identifier, datatype=XSD.string)))
    if metric.metric_name:
        g.add((instance_uri, RDFS.label, Literal(metric.metric_name)))
    if metric.timestamp:
        g.add((instance_uri, CORONA.observedAt, format_rdflib_literal(metric.timestamp)))
    if metric.source_entity_uri:
        try:
            source_uri = URIRef(metric.source_entity_uri)
            g.add((instance_uri, CORONA.metricSource, source_uri))
        except Exception as e:
             pytest.fail(f"Could not create URIRef from source_entity_uri '{metric.source_entity_uri}': {e}")
    elif metric.source_entity_address:
        g.add((instance_uri, CORONA.sourceAddress, Literal(metric.source_entity_address)))

    metric_fields = metric._get_metric_fields()
    for field_name, value in metric_fields.items():
        if value is None:
            continue

        pydantic_field = metric.model_fields.get(field_name)
        prop_name_camel = pydantic_field.alias if pydantic_field and pydantic_field.alias else to_camel_case(field_name)
        namespace = BACNET if "bacnet" in field_name.lower() or any(term in prop_name_camel.lower() for term in ["who", "cov", "bbmd", "readproperty", "iam", "ihave", "routed", "forwarded"]) else CORONA
        prop_uri = namespace[prop_name_camel]
        g.add((instance_uri, prop_uri, format_rdflib_literal(value)))

# --- Test Function ---

# Define path to shapes file relative to project root
SHAPES_FILE_PATH = os.path.join(project_root, "data/corona-shapes.ttl")
ONTOLOGY_FILE_PATH = os.path.join(project_root, "data/corona-ontology.ttl") # Needed for inference

@pytest.fixture(scope="module")
def shapes_graph():
    """Fixture to load the SHACL shapes graph once per module."""
    if not os.path.exists(SHAPES_FILE_PATH):
        pytest.fail(f"SHACL shapes file not found at: {SHAPES_FILE_PATH}")
    g = Graph()
    try:
        g.parse(SHAPES_FILE_PATH, format="turtle")
        return g
    except Exception as e:
        pytest.fail(f"Error parsing SHACL shapes file: {e}")

@pytest.fixture(scope="module")
def ontology_graph():
    """Fixture to load the ontology graph once per module."""
    if not os.path.exists(ONTOLOGY_FILE_PATH):
        # Ontology might be optional for basic validation but needed for inference
        print(f"Warning: Ontology file not found at: {ONTOLOGY_FILE_PATH}. RDFS inference might be limited.")
        return None # Allow tests to proceed without ontology if desired
        # Or uncomment below to fail if ontology is strictly required
        # pytest.fail(f"Ontology file not found at: {ONTOLOGY_FILE_PATH}")
    g = Graph()
    try:
        g.parse(ONTOLOGY_FILE_PATH, format="turtle")
        return g
    except Exception as e:
        pytest.fail(f"Error parsing ontology file: {e}")


def test_demo_metrics_ttl_validation(shapes_graph, ontology_graph):
    """
    Tests that the TTL generated from all demo metrics validates against the SHACL shapes.
    """
    # 1. Generate demo metrics
    demo_metrics_list = generate_all_sample_metrics()
    assert len(demo_metrics_list) > 0, "No demo metrics were generated."

    # 2. Create a combined data graph
    data_graph = Graph()
    data_graph.bind("corona", CORONA)
    data_graph.bind("bacnet", BACNET)
    data_graph.bind("xsd", XSD)
    data_graph.bind("rdf", RDF)
    data_graph.bind("rdfs", RDFS)

    for metric in demo_metrics_list:
        add_metric_to_graph(metric, data_graph)

    assert len(data_graph) > 0, "Data graph is empty after adding metrics."

    # 3. Perform SHACL validation
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph, # Provide ontology for inference if loaded
        inference='rdfs' if ontology_graph else 'none', # Use RDFS inference if ontology is available
        abort_on_first=False,
        allow_infos=False,
        debug=False
    )

    # 4. Assert conformance
    assert conforms, f"Validation failed. Results:\n{results_text}"
