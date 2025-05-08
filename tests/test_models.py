import pytest
from rdflib import Graph
from pyshacl import validate
import os
from datetime import datetime

# Adjust import path based on project structure
from corona_framework.models import BacnetApplicationMetric, COVNotificationMetric, RouterBBMDMetric
from corona_framework.constants import CORONA, BACNET # Assuming constants are needed

# Determine project root and paths relative to the test file
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir) # Go up one level from tests/ to project root

shapes_file_path = os.path.join(project_root, "data", "corona-shapes.ttl")
ontology_path = os.path.join(project_root, "data", "corona-ontology.ttl") # Needed for RDFS inference

# --- Fixtures ---

@pytest.fixture(scope="module")
def shapes_graph():
    """Loads the SHACL shapes graph once per module."""
    graph = Graph()
    try:
        graph.parse(shapes_file_path, format="turtle")
        print(f"\nLoaded SHACL shapes from {shapes_file_path} ({len(graph)} triples)")
        return graph
    except Exception as e:
        pytest.fail(f"Failed to load SHACL shapes from {shapes_file_path}: {e}")

@pytest.fixture(scope="module")
def ontology_graph():
    """Loads the ontology graph once per module for inference."""
    graph = Graph()
    try:
        graph.parse(ontology_path, format="turtle")
        print(f"Loaded Ontology from {ontology_path} ({len(graph)} triples)")
        return graph
    except Exception as e:
        pytest.fail(f"Failed to load ontology from {ontology_path}: {e}")


# --- Helper Function ---

def validate_rdf(ttl_data: str, shapes_graph: Graph, ontology_graph: Graph):
    """Validates RDF data (in Turtle string) against shapes."""
    data_graph = Graph()
    try:
        data_graph.parse(data=ttl_data, format="turtle")
    except Exception as e:
        pytest.fail(f"Failed to parse generated TTL data: {e}\nData:\n{ttl_data}")

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph, # Provide ontology for inference if needed
        inference='rdfs',       # Enable RDFS inference
        debug=False,
        meta_shacl=False        # Depending on your shapes, might need adjustment
    )
    assert conforms, f"SHACL validation failed:\n{results_text}"


# --- Test Cases ---

def test_bacnet_application_metric(shapes_graph, ontology_graph):
    """Tests BacnetApplicationMetric instantiation and SHACL validation."""
    timestamp = datetime.now()
    metric_data = {
        "metric_instance_uri": f"urn:corona:metric:bacnetApp:dev1:{int(timestamp.timestamp())}",
        "source_entity_uri": "urn:corona:device:bacnetDevice1",
        "source_entity_address": "192.168.1.100",
        "observed_from": "urn:corona:observer:captureAgent1", # Use a URN or valid IRI
        "description": "BACnet application metrics for Device 1",
        "metric_identifier": "bacnet_app_dev1",
        "metric_name": "BACnet App Stats (Dev1)",
        "timestamp": timestamp,
        "readPropertyRequests": 150,
        "readPropertyResponses": 148,
        "who_is_requests_sent": 10,
        "global_who_is_requests_sent": 8,
        "directed_who_is_requests_sent": 2,
        "i_am_responses_received": 5,
        "total_bacnet_messages_sent": 200,
        "total_broadcasts_received": 15
    }
    try:
        metric_instance = BacnetApplicationMetric(**metric_data)
    except Exception as e:
        pytest.fail(f"Failed to instantiate BacnetApplicationMetric: {e}")

    ttl_output = metric_instance.to_ttl()
    print(f"\nGenerated TTL for BacnetApplicationMetric:\n{ttl_output}") # Print for debugging
    validate_rdf(ttl_output, shapes_graph, ontology_graph)


def test_cov_notification_metric(shapes_graph, ontology_graph):
    """Tests COVNotificationMetric instantiation and SHACL validation."""
    timestamp = datetime.now()
    metric_data = {
        "metric_instance_uri": f"urn:corona:metric:cov:dev2:{int(timestamp.timestamp())}",
        "source_entity_uri": "urn:corona:device:bacnetDevice2",
        "source_entity_address": "192.168.1.101",
        "observed_from": "urn:corona:observer:analyzerX", # Use a URN or valid IRI
        "timestamp": timestamp,
        "unconfirmed_cov_notifications_sent": 500,
        "confirmed_cov_notifications_received": 20,
        "confirmed_cov_notifications_sent": 10, # Add more fields
        "unconfirmed_cov_notifications_received": 450
    }
    try:
        metric_instance = COVNotificationMetric(**metric_data)
    except Exception as e:
        pytest.fail(f"Failed to instantiate COVNotificationMetric: {e}")

    ttl_output = metric_instance.to_ttl()
    print(f"\nGenerated TTL for COVNotificationMetric:\n{ttl_output}") # Print for debugging
    validate_rdf(ttl_output, shapes_graph, ontology_graph)


def test_router_bbmd_metric(shapes_graph, ontology_graph):
    """Tests RouterBBMDMetric instantiation and SHACL validation."""
    timestamp = datetime.now()
    metric_data = {
        "metric_instance_uri": f"urn:corona:metric:router:gw1:{int(timestamp.timestamp())}",
        "source_entity_uri": "urn:corona:device:gateway1",
        "source_entity_address": "10.0.0.1",
        "observed_from": "urn:corona:observer:monitorService", # Use a URN or valid IRI
        "timestamp": timestamp,
        "messages_routed": 10000,
        "messages_forwarded": 500,
        "routed_devices_seen": 25,
        "bbmd_entries_count": 10,
        "foreign_device_registrations": 5, # Add more fields
        "routed_messages_sent": 9500,
        "routed_messages_received": 480
    }
    try:
        metric_instance = RouterBBMDMetric(**metric_data)
    except Exception as e:
        pytest.fail(f"Failed to instantiate RouterBBMDMetric: {e}")

    ttl_output = metric_instance.to_ttl()
    print(f"\nGenerated TTL for RouterBBMDMetric:\n{ttl_output}") # Print for debugging
    validate_rdf(ttl_output, shapes_graph, ontology_graph)

# Add more tests for edge cases if needed (e.g., minimal data)

def test_bacnet_application_metric_minimal(shapes_graph, ontology_graph):
    """Tests BacnetApplicationMetric with minimal required data."""
    timestamp = datetime.now()
    metric_data = {
        "metric_instance_uri": f"urn:corona:metric:bacnetApp:devMin:{int(timestamp.timestamp())}",
        # observed_from is required by base shape
        "observed_from": "urn:corona:observer:minimalObserver",
        "timestamp": timestamp,
        # Add at least one actual metric value if applicable to the class shape
        "readPropertyRequests": 1 # Example value
    }
    try:
        metric_instance = BacnetApplicationMetric(**metric_data)
    except Exception as e:
        pytest.fail(f"Failed to instantiate minimal BacnetApplicationMetric: {e}")

    ttl_output = metric_instance.to_ttl()
    print(f"\nGenerated TTL for minimal BacnetApplicationMetric:\n{ttl_output}")
    validate_rdf(ttl_output, shapes_graph, ontology_graph)

