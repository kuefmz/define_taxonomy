import json
import os

def select_best_matches(matches):
    best_matches_openaire = {}
    best_matches_openalex = {}
    
    for match in matches:
        openaire_category = match["openaire"]
        openalex_category = match["openalex"]
        similarity = match["similarity"]
        
        if openaire_category not in best_matches_openaire or similarity > best_matches_openaire[openaire_category]["similarity"]:
            best_matches_openaire[openaire_category] = match
        
        if openalex_category not in best_matches_openalex or similarity > best_matches_openalex[openalex_category]["similarity"]:
            best_matches_openalex[openalex_category] = match
    
    return best_matches_openalex, best_matches_openaire


def main():
	json_folder_path = 'data/'
    
	for filename in os.listdir(json_folder_path):
		print(f'Processing file: {filename}')
		page = filename.split('output_')[-1].replace('.json', '')
		if filename.endswith('.json'):
			json_file_path = os.path.join(json_folder_path, filename)
			with open(json_file_path, 'r') as file:
				data = json.load(file)
				for title, details in data.items():
					matches = []
					matches += details['exact_matches']
					matches += details['similarity']
					matches += details['missmatches']
     
					best_matches_openalex, best_matches_openaire = select_best_matches(matches)
                    
					data[title]['best_matches_openalex'] = best_matches_openalex
					data[title]['best_matches_openaire'] = best_matches_openaire
					
			with open(f'data/preprocessed_output/output_{page}.json', 'a+') as f:  
				f.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()