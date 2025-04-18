from rdflib import Graph
from pyshacl import validate
import sys

# File paths
example_model_path = "corona-ASHRAE135ct.ttl"
shapes_file_path = "corona-shapes.ttl"

def validate_model():
    # Load the example model
    data_graph = Graph()
    try:
        data_graph.parse(example_model_path, format="turtle")
    except Exception as e:
        print("An error occurred while processing the validation results:")
        print(f"Error: {e}")
        sys.exit(1)

    # Load the SHACL shapes
    shapes_graph = Graph()
    shapes_graph.parse(shapes_file_path, format="turtle")

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

if __name__ == "__main__":
    validate_model()