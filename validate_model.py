from rdflib import Graph, Namespace, RDF, RDFS
from pyshacl import validate
import sys

# File paths - get absolute paths based on script location
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
example_model_path = os.path.join(script_dir, "corona-ASHRAE135ct.ttl")
shapes_file_path = os.path.join(script_dir, "corona-shapes.ttl")
ontology_path = os.path.join(script_dir, "corona-ontology.ttl")

# Define Corona namespace
CORONA = Namespace("http://example.org/standards/corona/metrics#")

def print_usage():
    """Print the usage information for the script."""
    print("Usage: python validate_model.py [OPTIONS] [MODEL_FILE]")
    print("\nOptions:")
    print("  --help              Show this help message and exit")
    print("  --analyze           Analyze the Corona ontology and print metrics statistics")
    print("\nArguments:")
    print("  MODEL_FILE          Path to the Turtle (.ttl) model file to validate")
    print("                      If not provided, defaults to corona-ASHRAE135ct.ttl")
    print("\nExamples:")
    print("  python validate_model.py                       # Validate the default model")
    print("  python validate_model.py --analyze             # Validate default model and analyze ontology")
    print("  python validate_model.py path/to/metrics.ttl   # Validate a custom model file")
    print("  python validate_model.py metrics.ttl --analyze # Validate custom model and analyze ontology")

def validate_model():
    # Check if a custom model file was provided as an argument
    custom_model_path = None
    analyze_flag = False
    
    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if arg == "--analyze":
            analyze_flag = True
        elif arg == "--help":
            print_usage()
            sys.exit(0)
        elif not arg.startswith('--'):
            custom_model_path = arg
    
    # Use the custom model path if provided, otherwise use the default
    model_path = custom_model_path if custom_model_path else example_model_path
    
    # Load the model to validate
    data_graph = Graph()
    try:
        data_graph.parse(model_path, format="turtle")
        print(f"Loaded model from {model_path}")
        print(f"Model contains {len(data_graph)} triples")
    except Exception as e:
        print("An error occurred while processing the model file:")
        print(f"Error: {e}")
        sys.exit(1)

    # Load the SHACL shapes
    shapes_graph = Graph()
    try:
        shapes_graph.parse(shapes_file_path, format="turtle")
        print(f"Loaded SHACL shapes from {shapes_file_path}")
        print(f"Shapes graph contains {len(shapes_graph)} triples")
    except Exception as e:
        print("An error occurred while processing the shapes file:")
        print(f"Error: {e}")
        sys.exit(1)

    # Perform validation
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",  # Enable RDFS reasoning
        debug=False
    )

    # Print results
    if conforms:
        print("Validation successful! The data conforms to the SHACL shapes.")
    else:
        print("Validation failed. See details below:")
        print(results_text)
    
    # Additional ontology analysis
    if analyze_flag:
        analyze_ontology()

def analyze_ontology():
    """Analyze the Corona ontology and print metrics statistics."""
    print("\n--- Corona Ontology Analysis ---")
    
    # Load the ontology
    ontology_graph = Graph()
    try:
        ontology_graph.parse(ontology_path, format="turtle")
        print(f"Successfully loaded the Corona ontology.")
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

if __name__ == "__main__":
    # Check for help flag directly
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_usage()
        sys.exit(0)
    
    validate_model()