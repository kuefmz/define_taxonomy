import json
import os
import spacy
from utils.utils import preprocess_term, preprocess_title

def select_best_matches(matches):
	best_matches_openaire = {}
	best_matches_openalex = {}
    
	for match in matches:
		match["openalex"] = preprocess_term(match["openalex"])
		match["openaire"] = preprocess_term(match["openaire"])
		openaire_category = match["openaire"]
		openalex_category = match["openalex"]
		if not openaire_category or not openalex_category or match["similarity"] <= 0:
			continue
		similarity = match["similarity"]
        
		if openaire_category not in best_matches_openaire or similarity > best_matches_openaire[openaire_category]["similarity"]:
			best_matches_openaire[openaire_category] = match
        
		if openalex_category not in best_matches_openalex or similarity > best_matches_openalex[openalex_category]["similarity"]:
			best_matches_openalex[openalex_category] = match
    
	return best_matches_openalex, best_matches_openaire


def calculcate_similarity_matches(openalex_terms, openaire_terms, nlp):
	matches = []
	for openalex_term in openalex_terms:
		for openaire_term in openaire_terms:
			if not openaire_term or not openalex_term:
				continue
			doc1 = nlp(openaire_term)
			doc2 = nlp(openalex_term)
			similarity = doc1.similarity(doc2)
			if similarity <= 0.0:
				continue
			match = {
				'openaire': openaire_term,
				'openalex': openalex_term,
				'similarity': similarity
			}
			matches.append(match)
	return matches



def main(new_data = False):
	json_folder_path = 'data/mapped_papers_per_page'
	nlp = spacy.load("en_core_web_md")
    
	for filename in os.listdir(json_folder_path):
		print(f'Processing file: {filename}')
		page = filename.split('output_')[-1].replace('.json', '')
		if filename.endswith('.json'):
			json_file_path = os.path.join(json_folder_path, filename)
			cnt = 1
			with open(json_file_path, 'r') as file:
				data = json.load(file)
				data_new = {}
				for title, details in data.items():
					title = preprocess_title(title)
					categories_openalex = details['openalex'].split(" | ")
					categories_openaire = details['openaire'].split(" | ")
					categories_openalex = [preprocess_term(x) for x in categories_openalex]
					categories_openaire = [preprocess_term(x) for x in categories_openaire]
					categories_openalex = [x for x in categories_openalex if x]
					categories_openaire = [x for x in categories_openaire if x]
					if new_data:
						matches = calculcate_similarity_matches(categories_openalex, categories_openaire, nlp)
					else:
						matches = []
						matches += details['exact_matches']
						matches += details['similarity']
						matches += details['missmatches']
						#details.pop('exact_matches', None)
						#details.pop('similarity', None)
						#details.pop('missmatches', None)
						#details.pop('openalex', None)
						#details.pop('openaire', None)
						#details['openalex'] = categories_openalex
						#details['openaire'] = categories_openaire
					#print(f'Similarity matches done {cnt}')
					cnt += 1
					best_matches_openalex, best_matches_openaire = select_best_matches(matches)
                    
					data_new[title] = {}
					data_new[title]['openalex'] = categories_openalex
					data_new[title]['openaire'] = categories_openaire
					data_new[title]['best_matches_openalex'] = best_matches_openalex
					data_new[title]['best_matches_openaire'] = best_matches_openaire
					
			with open(f'data/papers_with_openalex_and_openaire_categories_aligned/output_{page}.json', 'a+') as f:  
				f.write(json.dumps(data_new, indent=4))


if __name__ == "__main__":
    main()