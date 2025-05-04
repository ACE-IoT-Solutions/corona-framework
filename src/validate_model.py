from rdflib import Graph, RDF, RDFS
from pyshacl import validate
import os
from typing import Optional
from constants import CORONA

# File paths - get absolute paths based on script location
script_dir = os.path.dirname(os.path.abspath(__file__)) # src directory
project_root = os.path.dirname(script_dir) # Project root

# Updated paths to data and examples directories
example_model_path = os.path.join(project_root, "examples", "corona-ASHRAE135ct.ttl")
shapes_file_path = os.path.join(project_root, "data", "corona-shapes.ttl")
ontology_path = os.path.join(project_root, "data", "corona-ontology.ttl")

def validate_model(model_path: Optional[str] = None, analyze_flag: bool = False):
    """Validates a given model file against SHACL shapes and optionally analyzes the ontology."""
    # Use the provided model path if available, otherwise use the default example
    effective_model_path = model_path if model_path else example_model_path

    # Ensure paths are absolute or correctly relative to the project root
    # (The paths defined above using project_root should already be correct)
    current_shapes_file_path = shapes_file_path
    current_ontology_path = ontology_path

    # Load the model to validate
    data_graph = Graph()
    try:
        data_graph.parse(effective_model_path, format="turtle")
        print(f"Loaded model from {effective_model_path}")
        print(f"Model contains {len(data_graph)} triples")
    except Exception as e:
        print(f"An error occurred while processing the model file: {effective_model_path}")
        print(f"Error: {e}")
        return  # Return instead of sys.exit

    # Load the SHACL shapes
    shapes_graph = Graph()
    try:
        shapes_graph.parse(current_shapes_file_path, format="turtle")
        print(f"Loaded SHACL shapes from {current_shapes_file_path}")
        print(f"Shapes graph contains {len(shapes_graph)} triples")
    except Exception as e:
        print(f"An error occurred while processing the shapes file: {current_shapes_file_path}")
        print(f"Error: {e}")
        return  # Return instead of sys.exit

    # Perform validation
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",  # Enable RDFS reasoning
        debug=False
    )

    # Print results
    if conforms:
        print("\nValidation successful! The data conforms to the SHACL shapes.")
    else:
        print("\nValidation failed. See details below:")
        print(results_text)

    # Additional ontology analysis
    if analyze_flag:
        analyze_ontology(current_ontology_path)  # Pass path to analyze_ontology

def analyze_ontology(ont_path: str = ontology_path):
    """Analyze the Corona ontology and print metrics statistics."""
    print("\n--- Corona Ontology Analysis ---")

    # Use the provided ontology path if available, otherwise use the default
    effective_ont_path = ont_path if ont_path else ontology_path

    # Load the ontology
    ontology_graph = Graph()
    try:
        ontology_graph.parse(effective_ont_path, format="turtle")
        print(f"Successfully loaded the Corona ontology from {effective_ont_path}.")
        print(f"Ontology contains {len(ontology_graph)} triples.")
    except Exception as e:
        print(f"Error loading ontology: {e}")
        return

    # Count metrics by type
    count_metrics(ontology_graph)
    
    # List general metric properties
    list_general_metric_properties(ontology_graph)
    
    # List message count metrics
    list_message_count_metrics(ontology_graph)
    
    # List router-related metrics
    list_router_metrics(ontology_graph)
    
    # List BBMD-related metrics
    list_bbmd_metrics(ontology_graph)
    
    # List broadcast-related metrics
    list_broadcast_metrics(ontology_graph)
    
    # List COV notification metrics
    list_cov_metrics(ontology_graph)
    
    # List Who* service metrics (WhoIs and WhoHas)
    list_who_metrics(ontology_graph)

def count_metrics(graph):
    """Count the different types of metrics in the graph."""
    # Network interface metrics
    network_metrics = list(graph.subjects(predicate=RDFS.subPropertyOf, 
                                        object=CORONA.NetworkInterfaceMetric))
    print(f"Network interface metrics: {len(network_metrics)}")
    
    # Application metrics with domain ApplicationMetric
    app_metrics = list(graph.subjects(predicate=RDFS.domain, 
                                   object=CORONA.ApplicationMetric))
    print(f"Application metrics: {len(app_metrics)}")
    
    # Lifetime metrics
    lifetime_metrics = list(graph.subjects(predicate=RDFS.subPropertyOf, 
                                        object=CORONA.LifetimeMetric))
    print(f"Lifetime metrics: {len(lifetime_metrics)}")

def list_router_metrics(graph):
    """List all router-related metrics."""
    print("\n=== Router-Related Metrics ===")
    
    router_metrics = []
    
    # Find metrics with 'routed' or 'messagesRouted' in their name
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        if 'routed' in str(s).lower() or 'messagesRouted' in str(s):
            # Get the label if available
            labels = list(graph.objects(s, RDFS.label))
            label = labels[0] if labels else "No label"
            
            # Get the comment if available
            comments = list(graph.objects(s, RDFS.comment))
            comment = comments[0] if comments else "No description"
            
            router_metrics.append((s, label, comment))
    
    # Sort by name and print
    for s, label, comment in sorted(router_metrics, key=lambda x: str(x[0])):
        print(f"  - {s}")
        print(f"    Label: {label}")
        print(f"    Description: {comment}")
        print()

def list_bbmd_metrics(graph):
    """List all BBMD-related metrics."""
    print("\n=== BBMD-Related Metrics ===")
    
    bbmd_metrics = []
    
    # Find metrics with 'forwarded' in their name
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        if 'forwarded' in str(s).lower():
            # Get the label if available
            labels = list(graph.objects(s, RDFS.label))
            label = labels[0] if labels else "No label"
            
            # Get the comment if available
            comments = list(graph.objects(s, RDFS.comment))
            comment = comments[0] if comments else "No description"
            
            bbmd_metrics.append((s, label, comment))
    
    # Sort by name and print
    for s, label, comment in sorted(bbmd_metrics, key=lambda x: str(x[0])):
        print(f"  - {s}")
        print(f"    Label: {label}")
        print(f"    Description: {comment}")
        print()

def list_broadcast_metrics(graph):
    """List all broadcast-related metrics."""
    print("\n=== Broadcast-Related Metrics ===")
    
    broadcast_metrics = []
    
    # Find metrics with 'broadcast' in their name
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        if 'broadcast' in str(s).lower():
            # Get the label if available
            labels = list(graph.objects(s, RDFS.label))
            label = labels[0] if labels else "No label"
            
            # Get the comment if available
            comments = list(graph.objects(s, RDFS.comment))
            comment = comments[0] if comments else "No description"
            
            broadcast_metrics.append((s, label, comment))
    
    # Sort by name and print
    for s, label, comment in sorted(broadcast_metrics, key=lambda x: str(x[0])):
        print(f"  - {s}")
        print(f"    Label: {label}")
        print(f"    Description: {comment}")
        print()

def list_cov_metrics(graph):
    """List all COV notification-related metrics."""
    print("\n=== COV Notification Metrics ===")
    
    cov_metrics = []
    
    # Find metrics with 'COVNotification' in their name
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        if 'COVNotification' in str(s):
            # Get the label if available
            labels = list(graph.objects(s, RDFS.label))
            label = labels[0] if labels else "No label"
            
            # Get the comment if available
            comments = list(graph.objects(s, RDFS.comment))
            comment = comments[0] if comments else "No description"
            
            cov_metrics.append((s, label, comment))
    
    # Sort by name and print
    for s, label, comment in sorted(cov_metrics, key=lambda x: str(x[0])):
        print(f"  - {s}")
        print(f"    Label: {label}")
        print(f"    Description: {comment}")
        print()

def list_who_metrics(graph):
    """List all Who* service-related metrics."""
    print("\n=== Who* Service Metrics ===")
    
    who_metrics = []
    
    # Find metrics with 'Who' in their name
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        if 'Who' in str(s):
            # Get the label if available
            labels = list(graph.objects(s, RDFS.label))
            label = labels[0] if labels else "No label"
            
            # Get the comment if available
            comments = list(graph.objects(s, RDFS.comment))
            comment = comments[0] if comments else "No description"
            
            who_metrics.append((s, label, comment))
    
    # Sort by name and print
    for s, label, comment in sorted(who_metrics, key=lambda x: str(x[0])):
        print(f"  - {s}")
        print(f"    Label: {label}")
        print(f"    Description: {comment}")
        print()

def list_general_metric_properties(graph):
    """List all general metric properties."""
    print("\n=== General Metric Properties ===")
    
    general_properties = []
    
    # Find general metric properties
    general_property_names = ['observedFrom', 'description', 'metric-identifier', 'metric-name']
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        for prop_name in general_property_names:
            if prop_name in str(s):
                # Get the label if available
                labels = list(graph.objects(s, RDFS.label))
                label = labels[0] if labels else "No label"
                
                # Get the comment if available
                comments = list(graph.objects(s, RDFS.comment))
                comment = comments[0] if comments else "No description"
                
                general_properties.append((s, label, comment))
                break
    
    # Sort by name and print
    for s, label, comment in sorted(general_properties, key=lambda x: str(x[0])):
        print(f"  - {s}")
        print(f"    Label: {label}")
        print(f"    Description: {comment}")
        print()

def list_message_count_metrics(graph):
    """List all message count metrics."""
    print("\n=== Message Count Metrics ===")
    
    message_metrics = []
    
    # Find metrics with 'message' in their name
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        if 'message' in str(s).lower() or 'bacnetmessage' in str(s).lower():
            # Get the label if available
            labels = list(graph.objects(s, RDFS.label))
            label = labels[0] if labels else "No label"
            
            # Get the comment if available
            comments = list(graph.objects(s, RDFS.comment))
            comment = comments[0] if comments else "No description"
            
            message_metrics.append((s, label, comment))
    
    # Sort by name and print
    for s, label, comment in sorted(message_metrics, key=lambda x: str(x[0])):
        print(f"  - {s}")
        print(f"    Label: {label}")
        print(f"    Description: {comment}")
        print()