import click
import json
import sys
import os
from typing import List, Dict, Any
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Adjust Python path to find modules in src/
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir) # Add project root to path

# Assuming these imports are correct relative to the project structure
try:
    from src.models import BaseMetric, CORONA, BACNET, format_rdflib_literal, to_camel_case
    from src import demo_metrics
    from src import validate_model
except ImportError as e:
    print(f"Error importing modules: {e}", file=sys.stderr)
    print("Ensure the script is run from the project root directory (`corona-standard/`)", file=sys.stderr)
    sys.exit(1)

def add_metric_to_graph(metric: BaseMetric, g: Graph) -> None:
    """Adds the triples for a single metric instance to an existing RDFLib Graph."""
    try:
        instance_uri = URIRef(metric.metric_instance_uri)
    except Exception as e:
        print(f"Warning: Invalid metric_instance_uri '{metric.metric_instance_uri}': {e}", file=sys.stderr)
        return

    # Add type triple
    g.add((instance_uri, RDF.type, CORONA[metric.__class__.__name__]))

    # Add common fields
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
            print(f"Warning: Could not create URIRef from source_entity_uri '{metric.source_entity_uri}': {e}", file=sys.stderr)
    elif metric.source_entity_address:
        g.add((instance_uri, CORONA.sourceAddress, Literal(metric.source_entity_address)))

    # Add specific metric value fields
    metric_fields = metric._get_metric_fields()
    for field_name, value in metric_fields.items():
        if value is None:
            continue

        pydantic_field = metric.model_fields.get(field_name)
        prop_name_camel = pydantic_field.alias if pydantic_field and pydantic_field.alias else to_camel_case(field_name)
        namespace = BACNET if "bacnet" in field_name.lower() or any(term in prop_name_camel.lower() for term in ["who", "cov", "bbmd", "readproperty", "iam", "ihave", "routed", "forwarded"]) else CORONA
        prop_uri = namespace[prop_name_camel]
        g.add((instance_uri, prop_uri, format_rdflib_literal(value)))

@click.group()
def cli() -> None:
    """Corona Standard CLI Tool"""
    pass

@cli.command()
@click.option('--type', 'metric_type', type=click.Choice(['app', 'cov', 'router', 'all']), default='all', help='Type of sample metric(s) to generate.')
@click.option('--format', 'output_format', type=click.Choice(['ttl', 'haystack', 'prometheus', 'json']), default='ttl', help='Output format for the generated metrics.')
@click.option('-o', '--output', type=click.Path(dir_okay=False, writable=True), help='Optional file path to write the output to.')
def generate(metric_type: str, output_format: str, output: str | None) -> None:
    """Generate sample metrics and serialize them."""
    metrics: List[BaseMetric] = []
    if metric_type == 'all':
        metrics = demo_metrics.generate_all_sample_metrics()
    elif metric_type == 'app':
        metrics.append(demo_metrics.generate_sample_bacnet_app_metric())
    elif metric_type == 'cov':
        metrics.append(demo_metrics.generate_sample_cov_metric())
    elif metric_type == 'router':
        metrics.append(demo_metrics.generate_sample_router_metric())

    output_str = ""

    if output_format == 'ttl':
        combined_graph = Graph()
        combined_graph.bind("corona", CORONA)
        combined_graph.bind("bacnet", BACNET)
        combined_graph.bind("xsd", XSD)
        combined_graph.bind("rdf", RDF)
        combined_graph.bind("rdfs", RDFS)
        for metric in metrics:
            add_metric_to_graph(metric, combined_graph)
        output_str = combined_graph.serialize(format='turtle')
    elif output_format == 'haystack':
        output_dicts: List[Dict[str, Any]] = []
        for metric in metrics:
            output_dicts.extend(metric.to_haystack_json())
        output_str = json.dumps(output_dicts)

    else:
        output_lines: List[str] = []
        for metric in metrics:
            if output_format == 'prometheus':
                output_lines.extend(metric.to_prometheus())
            elif output_format == 'json':
                # Use model_dump_json for Pydantic v2 for direct JSON string output
                output_lines.append(json.loads(metric.model_dump_json())) # Parse back to dict for consistent list handling

        if output_format == 'haystack' or output_format == 'json':
            # Dump the list of dicts/objects as a single JSON array
            output_str = json.dumps(output_lines, indent=2)
        elif output_format == 'prometheus':
            output_str = "\n".join(output_lines) # Keep as separate lines

    if output:
        try:
            with open(output, 'w') as f:
                f.write(output_str)
            click.echo(f"Output written to {output}")
        except IOError as e:
            click.echo(f"Error writing to file {output}: {e}", err=True)
    else:
        click.echo(output_str)

@cli.command()
@click.option('--file', 'model_file', type=click.Path(exists=True, dir_okay=False, readable=True), help='Path to the TTL model file to validate. Defaults to the example file.')
def validate(model_file: str | None) -> None:
    """Validate a metric model (TTL file) against SHACL shapes."""
    # Pass analyze_flag=False as default
    try:
        validate_model.validate_model(model_path=model_file, analyze_flag=False)
    except Exception as e:
        click.echo(f"Validation error: {e}", err=True)

@cli.command()
@click.option('--ontology', 'ontology_file', type=click.Path(exists=True, dir_okay=False, readable=True), help='Path to the ontology TTL file to analyze. Defaults to the one in validate_model.py.')
def analyze(ontology_file: str | None) -> None:
    """Analyze the Corona ontology structure."""
    try:
        validate_model.analyze_ontology(ont_path=ontology_file)
    except Exception as e:
        click.echo(f"Analysis error: {e}", err=True)

if __name__ == "__main__":
    cli()
