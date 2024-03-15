from neo4j import GraphDatabase
import csv
import json
import os

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__password))
        except Exception as e:
            print(f"Failed to create the driver: {e}")
    
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print(f"Query failed: {e}")
        finally:
            if session is not None:
                session.close()
        return response

def save_total_pairs_to_json(total_pairs, filename="total_pairs.json"):
    with open(filename, 'w') as f:
        json.dump({"total_pairs": total_pairs}, f)

# Function to load total pairs from a JSON file
def load_total_pairs_from_json(filename="total_pairs.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get("total_pairs", None)
    return None

# Connect to Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"
conn = Neo4jConnection(uri, user, password)
print('Connected')


input_file = "category_pairs.json"
output_file = "output.csv"

with open(input_file, 'r', encoding='utf-8-sig') as infile, open(output_file, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["Category1", "Source1", "Category2", "Source2", "Similarity", "PapersInC1", "PapersInC2", "PapersInBoth"])
    category_pairs = json.load(infile)

    for pair in category_pairs:
        c1_name = pair["Category1"]
        c1_source = pair["Source1"]
        c2_name = pair["Category2"]
        c2_source = pair["Source2"]
        similarity = pair['Similarity']

        c1_papers_query = "MATCH (p:Paper)-[:BELONGS_TO_CATEGORY]->(c:Category {category_name: $category_name, source: $source}) RETURN count(p) AS count"
        c1_papers_result = conn.query(c1_papers_query, parameters={"category_name": c1_name, "source": c1_source})
        papers_in_c1 = c1_papers_result[0]["count"] if c1_papers_result else 0

        # Fetch papers in C2
        c2_papers_query = "MATCH (p:Paper)-[:BELONGS_TO_CATEGORY]->(c:Category {category_name: $category_name, source: $source}) RETURN count(p) AS count"
        c2_papers_result = conn.query(c2_papers_query, parameters={"category_name": c2_name, "source": c2_source})
        papers_in_c2 = c2_papers_result[0]["count"] if c2_papers_result else 0

        # Fetch papers in both C1 and C2
        both_papers_query = """
        MATCH (p:Paper)-[:BELONGS_TO_CATEGORY]->(c1:Category {category_name: $category1, source: $source1}),
              (p)-[:BELONGS_TO_CATEGORY]->(c2:Category {category_name: $category2, source: $source2})
        RETURN count(p) AS count
        """
        both_papers_result = conn.query(both_papers_query, parameters={"category1": c1_name, "source1": c1_source, "category2": c2_name, "source2": c2_source})
        papers_in_both = both_papers_result[0]["count"] if both_papers_result else 0

        writer.writerow([c1_name, c1_source, c2_name, c2_source, similarity, papers_in_c1, papers_in_c2, papers_in_both])


# Close the Neo4j connection
conn.close()
