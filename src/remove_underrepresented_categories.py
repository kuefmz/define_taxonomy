import os
import json

# Paths to your folders and text files containing the category sets
json_folder = 'data/papers_with_openalex_and_openaire_categories_aligned'
filtered_json_folder = 'data/remove_underrepresented_categories'
openalex_categories_file = 'data/openalex_categories_appeared_more_then_10_times.txt'
openaire_categories_file = 'data/openaire_categories_appeared_more_then_10_times.txt'

# Read the categories from the text files and store them in sets
with open(openalex_categories_file, 'r') as file:
    openalex_categories_set = {line.strip() for line in file if line.strip()}

with open(openaire_categories_file, 'r') as file:
    openaire_categories_set = {line.strip() for line in file if line.strip()}


filenames = os.listdir(json_folder)
filenames.sort()
for file in filenames:
    if file.endswith(".json"):
        print(f'Processing: {file}')
        file_path = os.path.join(json_folder, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            filtered_data = {}
            for paper, content in data.items():
                # Filter OpenAlex and OpenAIRE categories
                filtered_openalex = [cat for cat in content.get('openalex', []) if cat in openalex_categories_set]
                filtered_openaire = [cat for cat in content.get('openaire', []) if cat in openaire_categories_set]

                best_matches_openalex = {}
                for cat, match in content['best_matches_openalex'].items():
                    if cat in openalex_categories_set:
                        best_matches_openalex[cat] = match
                best_matches_openaire = {}
                for cat, match in content['best_matches_openaire'].items():
                    if cat in openaire_categories_set:
                        best_matches_openaire[cat] = match
                # Update the JSON only if there are relevant categories
                if filtered_openalex or filtered_openaire:
                    filtered_data[paper] = {
                        'openalex': filtered_openalex,
                        'openaire': filtered_openaire,
                        'best_matches_openalex': best_matches_openalex,
                        'best_matches_openaire': best_matches_openaire,
                    }

            if filtered_data:
                filtered_file_path = os.path.join(filtered_json_folder, file)
                with open(filtered_file_path, 'w') as fw:
                    json.dump(filtered_data, fw, indent=4)


