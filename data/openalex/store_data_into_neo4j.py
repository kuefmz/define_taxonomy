import json
import os
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

class Neo4jLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_json_data(self, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            self.create_data_in_neo4j(data)
            
    def preprocess_term(self, term):
        # Split the term into words and filter out numeric-only words
        filtered_words = [word.lower() for word in term.split(' ') if not word.isnumeric()]
        # Rejoin the words to form the preprocessed term
        preprocessed_term = ' '.join(filtered_words)
        return preprocessed_term

    def create_data_in_neo4j(self, data):
        with self.driver.session() as session:
            for title, details in data.items():
                categories_openalex = details['openalex'].split(" | ")
                categories_openaire = details['openaire'].split(" | ")
                categories_openalex = [self.preprocess_term(x) for x in categories_openalex]
                categories_openaire = [self.preprocess_term(x) for x in categories_openaire]
                exact_matches = details['exact_matches']
                similarity = details['similarity']
                missmatches = details['missmatches']

                # Create Paper node
                session.write_transaction(self.create_paper, title)

                # Create Category nodes and relationships
                for category in categories_openalex:
                    session.write_transaction(self.create_category, category, 'OpenAlex')
                    session.write_transaction(self.link_paper_to_category, title, category, 'OpenAlex')
                for category in categories_openaire:
                    session.write_transaction(self.create_category, category, 'OpenAIRE')
                    session.write_transaction(self.link_paper_to_category, title, category, 'OpenAIRE')

                # Create similarity relationships between categories

                for match in exact_matches:
                    session.write_transaction(self.create_similarity_relationship, match['openaire'], match['openalex'], match['similarity'])
                for match in similarity:
                    session.write_transaction(self.create_similarity_relationship, match['openaire'], match['openalex'], match['similarity'])
                for match in missmatches:
                    session.write_transaction(self.create_similarity_relationship, match['openaire'], match['openalex'], match['similarity'])

    @staticmethod
    def create_paper(tx, title):
        query = (
            "MERGE (p:Paper {title: $title})"
        )
        tx.run(query, title=title)
        #print(f"Paper created: {'title'}")

    @staticmethod
    def create_category(tx, category, source):
        query = (
            "MERGE (c:Category {category_name: $category, source: $source})"
        )
        tx.run(query, category=category, source=source)
        #print(f"Category created: {category} with source {source}")

    @staticmethod
    def link_paper_to_category(tx, paper_title, category_name, source):
        query = (
            "MATCH (p:Paper {title: $paper_title}), "
            "(c:Category {category_name: $category_name, source: $source}) "
            "MERGE (p)-[:BELONGS_TO_CATEGORY]->(c)"
        )
        tx.run(query, paper_title=paper_title, category_name=category_name, source=source)
        #print(f"Linked paper '{paper_title}' to category '{category_name}' with source {source}")
        

    @staticmethod
    def create_similarity_relationship(tx, category_openaire, category_openalex, similarity):
        query = """
            MATCH (c1:Category {category_name: $category_openaire, source: 'OpenAIRE'}), 
                  (c2:Category {category_name: $category_openalex, source: 'OpenAlex'})
            MERGE (c1)-[:SIMILAR {similarity: $similarity}]->(c2)
        """
        tx.run(query, category_openaire=category_openaire, category_openalex=category_openalex, similarity=similarity)
        #print(f"Linked categoty '{category_openaire}' to category '{category_openalex}' with similarity {similarity}")


def main():
    loader = Neo4jLoader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    json_folder_path = 'data/'
    
    for filename in os.listdir(json_folder_path):
        print(f'Processing file: {filename}')
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_folder_path, filename)
            loader.load_json_data(json_file_path)
    
    loader.close()

if __name__ == "__main__":
    main()