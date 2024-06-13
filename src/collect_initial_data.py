import requests
import xml.etree.ElementTree as ET
import time
from utils.utils import preprocess_term, preprocess_title
import json

openalex_works_api = "https://api.openalex.org/works?page=1&filter=concepts.id:C154945302&sort=cited_by_count:desc&per_page=200"
concept_base_url = "https://api.openalex.org/concepts/"
openaire_base_url = "https://api.openaire.eu/search/publications?title="


def get_openaire_subjects(response_text: str, orig_title: str):
	subjects = []
	tree = ET.fromstring(response_text)
	try:
		metadata = tree.findall('results')[0].findall('result')[0].findall('metadata')[0]
		subjects_xml = metadata.findall('{http://namespace.openaire.eu/oaf}entity')[0].findall('{http://namespace.openaire.eu/oaf}result')[0].findall('subject')
        #print('Subjects: ', subjects_xml)
		for subject in subjects_xml:
			if subject.text:
				subjects.append(subject.text)
	except:
		print(f'Not found: {orig_title}')
		return None

	return subjects


def get_openaire_subjects_from_title(title):
	title_words = title.split(' ')
	title_search_string = ""
	for word in title_words:
		word_clean = ''.join(x for x in word if x.isalpha())
		title_search_string += word_clean.lower() + ' '
	url = openaire_base_url+title_search_string
	response = requests.get(url)
	if response.status_code == 200:
		openaire_subjects = get_openaire_subjects(response.text, title)
		return openaire_subjects
	else:
		return None


def main():
	concept_id = 'C154945302' # AI
	sort_by = 'cited_by_count:desc'
	per_page = 200
	cursor = 'IlswLCA2OS4wLCAwLCAnaHR0cHM6Ly9vcGVuYWxleC5vcmcvVzQyNDg5NDM0NjInXSI='
    
	base_url = 'https://api.openalex.org/works'
	params = {
        'filter': f'concepts.id:{concept_id}',
        'sort': sort_by,
        'per_page': per_page,
        'cursor': cursor,
	}
	page_count = 49999 + 1
    
	while True:
		time.sleep(1)
		out_json = {}
		print(f'Fetching page: {page_count}')
		
		#url = openalex_works_api.replace('page=1', f'page={page}')
		response = requests.get(base_url, params=params)

		if response.status_code == 200:
			data = response.json()
			page_results = data['results']
			if True:
				with open(f'data/raw_openalex_api_outputs/page_{page_count}.json', 'a+') as f:
					json.dump(data, f, indent=4)
			
			page_results = []
			for work in page_results:
				cnt += 1
				print(f'Work count: {cnt}')
				if not work['title']:
					continue
				title = preprocess_title(work['title'])
				#print(work['title'])
				openalex_consepts = []
				for concept in work['concepts']:
					openalex_consepts.append(concept['display_name'])
				
	
				openaire_subjects = get_openaire_subjects_from_title(title)

				if not openaire_subjects:
					continue
				if not openalex_consepts:
					continue

				openalex_terms = []
				for openalex_term in openalex_consepts:
					preprocessed = preprocess_term(openalex_term)
					if preprocessed:
						openalex_terms.append(preprocessed)
				
				openaire_terms = []
				for openaire_term in openaire_subjects:
					preprocessed = preprocess_term(openaire_term)
					if preprocessed:
						openaire_terms.append(preprocessed)
				
				#print(f'OpenAlex: {openalex_terms}')
				#print(f'OpenAIRE: {openalex_terms}')
				out_json[title] = {}
				out_json[title]['openalex'] = openalex_terms
				out_json[title]['openaire'] = openaire_terms

		
			#with open(f'data/initial_collection/output_{page_count}.json', 'a+') as f:  
			#	f.write(json.dumps(out_json, indent=4))

			cursor = data.get('meta', {}).get('next_cursor')	
			if not cursor or cursor == '':
				break  # Exit loop if no more results
			params['cursor'] = cursor
			page_count += 1
		else:
			print(f"Failed to fetch data: {response.status_code}")
			break



if __name__ == "__main__":
    main()

