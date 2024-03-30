import os
import json
import requests

def process_json_file(folder_path, filename):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                for result in data['results']:
                    doi = result.get('doi')
                    if doi:
                        response = requests.get(f'https://api.openaire.eu/search/publications?doi={doi}')
                        if response.status_code == 200:
                            xml_data = response.text
                            # Save the XML data to a file
                            xml_filename = f"{result['id'].split('/')[-1]}.xml"
                            with open('data/raw_openaire_data/' + xml_filename, 'w') as xml_file:
                                xml_file.write(xml_data)
                        else:
                            print(f"Failed to fetch data for DOI {doi}")

if __name__ == "__main__":
    folder_path = 'data/raw_openalex_api_outputs'
    filenames = os.listdir(folder_path)
    filenames.sort()
    for filename in filenames:
    	process_json_file(folder_path, filename)