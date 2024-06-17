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
def add_work_to_graph(graph, work, categories_graph):
    work_uri = URIRef(work['id'])
    if (work_uri, None, None) not in graph:
        graph.add((work_uri, RDF.type, SCHEMA.ScholarlyArticle))
        graph.add((work_uri, SCHEMA.name, Literal(work['title'])))
        graph.add((work_uri, SCHEMA.identifier, Literal(work['doi'])))
        

        logging.info(f"Added new work to the graph: {work['title']}")
    else:
        logging.info(f"Work already exists in the graph: {work['title']}")


def add_category_to_graph(graph, work):
    work_uri = URIRef(work['id'])
    for concept in work.get('concepts', []):
        concept_uri = URIRef(concept['id'])
        graph.add((work_uri, SCHEMA.about, concept_uri))
        if (concept_uri, None, None) not in categories_graph:
            categories_graph.add((concept_uri, RDF.type, SCHEMA.Thing))
            categories_graph.add((concept_uri, SCHEMA.name, Literal(concept['display_name'])))

# Function to process a single JSON file
def process_json_file(json_file_path, graph):
    logging.info(f"Processing JSON file: {json_file_path}")
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Iterate through each work in the JSON and add to the RDF graph
        for work in data['results']:
            if 'title' in work:  # Ensure there is a title
                add_work_to_graph(graph, work, categories_graph)
            else:
                logging.warning(f"Skipping work with missing title: {work.get('id')}")
    except Exception as e:
        logging.error(f"Failed to process file {json_file_path}: {e}")

    return new_graph, categories_graph

# Function to save RDF graph to file
def save_graph_to_file(graph, base_path, prefix, count):
    file_path = os.path.join(base_path, f"{prefix}_{count}.rdf")
    with open(file_path, 'w') as rdf_file:
        rdf_file.write(graph.serialize(format='turtle'))
    logging.info(f"Saved graph to {file_path}")

# Main script execution
folder_path = '/home/jenifer/raw_openalex/'
papers_output_folder = '/home/jenifer/papers_rdf/'
categories_output_folder = '/home/jenifer/categories_rdf'
papers_prefix = 'papers'
categories_prefix = 'categories'


papers_graph = Graph()
papers_graph.namespace_manager.bind('schema', SCHEMA, override=True, replace=True)



paper_count = 0
category_count = 0
paper_batch_count = 0
category_batch_count = 0

for json_file_path in glob.glob(os.path.join(folder_path, '*.json')):
    new_graph = process_json_file(json_file_path, papers_graph)
    
    paper_count += len(new_graph)
    if paper_count >= 1000:
        paper_batch_count += 1
        save_graph_to_file(papers_graph, papers_output_folder, papers_prefix, paper_batch_count)
        papers_graph = Graph()
        papers_graph.namespace_manager.bind('schema', SCHEMA, override=True, replace=True)
        paper_count = 0


if paper_count > 0:
    paper_batch_count += 1
    save_graph_to_file(papers_graph, papers_output_folder, papers_prefix, paper_batch_count)


categories_graph = Graph()
categories_graph.namespace_manager.bind('schema', SCHEMA, override=True, replace=True)

for json_file_path in glob.glob(os.path.join(folder_path, '*.json')):
    categories_graph = process_json_file(json_file_path, categories_graph)

    category_count += len(categories_graph)
    if category_count >= 1000:
        category_batch_count += 1
        save_graph_to_file(categories_graph, categories_output_folder, categories_prefix, category_batch_count)
        categories_graph = Graph()
        categories_graph.namespace_manager.bind('schema', SCHEMA, override=True, replace=True)
        category_count = 0

if category_count > 0:
    category_batch_count += 1
    save_graph_to_file(categories_graph, categories_output_folder, categories_prefix, category_batch_count)

logging.info("All files processed")
