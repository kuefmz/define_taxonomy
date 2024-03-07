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
                categories_openalex = details['openalex']
                categories_openaire = details['openaire']
                best_matches_openalex = details['best_matches_openalex']
                best_matches_openaire = details['best_matches_openaire']

                # Create Paper node
                session.write_transaction(self.create_paper, title)

                # Create Category nodes and relationships
                for category in categories_openalex:
                    session.write_transaction(self.create_category, category, 'OpenAlex')
                    session.write_transaction(self.link_paper_to_category, title, category, 'OpenAlex')
                for category in categories_openaire:
                    session.write_transaction(self.create_category, category, 'OpenAIRE')
                    session.write_transaction(self.link_paper_to_category, title, category, 'OpenAIRE')

                for cat, match in best_matches_openalex.items():
                    session.write_transaction(self.create_similarity_relationship, match['openaire'], match['openalex'], match['similarity'])
                for cat, match in best_matches_openaire.items():
                    session.write_transaction(self.create_similarity_relationship, match['openaire'], match['openalex'], match['similarity'])



    @staticmethod
    def create_paper(tx, title):
        query = (
            "MERGE (p:Paper {title: $title})"
        )
        tx.run(query, title=title)

    @staticmethod
    def create_category(tx, category, source):
        #print(f"Category created: {category} with source {source}")
        query = (
            "MERGE (c:Category {category_name: $category, source: $source})"
        )
        tx.run(query, category=category, source=source)
        
    @staticmethod
    def link_paper_to_category(tx, paper_title, category_name, source):
        #print(f"Linked paper '{paper_title}' to category '{category_name}' with source {source}")
        query = (
            "MATCH (p:Paper {title: $paper_title}), "
            "(c:Category {category_name: $category_name, source: $source}) "
            "MERGE (p)-[:BELONGS_TO_CATEGORY]->(c)"
        )
        tx.run(query, paper_title=paper_title, category_name=category_name, source=source)
        

    @staticmethod
    def create_similarity_relationship(tx, category_openaire, category_openalex, similarity):
        #print(f"Linked categoty '{category_openaire}' to category '{category_openalex}' with similarity {similarity}")
        query = """
            MATCH (c1:Category {category_name: $category_openaire, source: 'OpenAIRE'}), 
                (c2:Category {category_name: $category_openalex, source: 'OpenAlex'})
            MERGE (c1)-[:SIMILAR {similarity: $similarity}]->(c2)
        """
        tx.run(query, category_openaire=category_openaire, category_openalex=category_openalex, similarity=similarity)


def main():
    loader = Neo4jLoader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    json_folder_path = 'data/remove_underrepresented_categories'
    
    filenames = os.listdir(json_folder_path)
    filenames.sort()
    for filename in filenames:
        print(f'Processing file: {filename}')
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_folder_path, filename)
            loader.load_json_data(json_file_path)
    
    loader.close()

if __name__ == "__main__":
    main()