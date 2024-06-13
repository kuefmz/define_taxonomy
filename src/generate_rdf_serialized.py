import json
import os
import glob
import logging
from rdflib import Graph, Literal, RDF, Namespace, URIRef
from filelock import FileLock

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define namespaces
SCHEMA = Namespace("http://schema.org/")

# Function to add a work to the graph
def add_work_to_graph(graph, work):
    work_uri = URIRef(work['id'])
    if (work_uri, None, None) not in graph:
        graph.add((work_uri, RDF.type, SCHEMA.ScholarlyArticle))
        graph.add((work_uri, SCHEMA.name, Literal(work['title'])))
        graph.add((work_uri, SCHEMA.identifier, Literal(work['doi'])))
        
        for concept in work.get('concepts', []):
            concept_uri = URIRef(concept['id'])
            graph.add((work_uri, SCHEMA.about, concept_uri))
            graph.add((concept_uri, SCHEMA.name, Literal(concept['display_name'])))
        logging.info(f"Added new work to the graph: {work['title']}")
    else:
        logging.info(f"Work already exists in the graph: {work['title']}")

    return graph

# Function to process a single JSON file
def process_json_file(json_file_path, graph):
    new_graph = Graph()

    # Bind the schema.org namespace to the prefix 'schema'
    new_graph.namespace_manager.bind('schema', SCHEMA, override=True, replace=True)

    logging.info(f"Processing JSON file: {json_file_path}")
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Iterate through each work in the JSON and add to the RDF graph
        for work in data['results']:
            if 'title' in work:  # Ensure there is a title
                new_graph = add_work_to_graph(new_graph, work)
            else:
                logging.warning(f"Skipping work with missing title: {work.get('id')}")
    except Exception as e:
        logging.error(f"Failed to process file {json_file_path}: {e}")

    return new_graph

# Main script execution
folder_path = '/path/to/your/json/folder'
rdf_file_path = 'data.rdf'
lock_file_path = rdf_file_path + '.lock'

# Ensure safe concurrent access to the RDF file using file locking
logging.info("Attempting to acquire file lock")
with FileLock(lock_file_path):
    logging.info("File lock acquired")
    
    # Load existing RDF file if it exists
    main_graph = Graph()
    if os.path.exists(rdf_file_path):
        logging.info(f"Loading existing RDF file: {rdf_file_path}")
        main_graph.parse(rdf_file_path, format='turtle')
    
    for json_file_path in glob.glob(os.path.join(folder_path, '*.json')):
        new_graph = process_json_file(json_file_path, main_graph)
        # Serialize only new triples to the RDF file
        with open(rdf_file_path, 'a') as rdf_file:
            rdf_file.write(new_graph.serialize(format='turtle').decode('utf-8'))
        main_graph += new_graph

    logging.info("All files processed")
