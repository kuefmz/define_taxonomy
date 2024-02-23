#!/usr/bin/env python
# coding: utf-8

# In[103]:


import pandas as pd
import requests
import xml.etree.ElementTree as ET
import json
import spacy
import time


# In[ ]:





# In[104]:


openalex_works_api = "https://api.openalex.org/works?page=1&filter=concepts.id:C154945302&sort=cited_by_count:desc&per_page=200"
concept_base_url = "https://api.openalex.org/concepts/"
openaire_base_url = "https://api.openaire.eu/search/publications?title="


# In[105]:


concept_id_name_json = {}
nlp = spacy.load("en_core_web_md")


# In[106]:


def get_concept_name_from_contept_id(concept_id: str):
    concept_id = concept_id.split('/')[-1]
    if concept_id in concept_id_name_json.keys():
        return concept_id_name_json[concept_id]
    else:
        url = concept_base_url + concept_id
        response = requests.get(url)
        if response.status_code == 200:
            concept_name = response.json()['display_name']
            concept_id_name_json[concept_id] = concept_name
            return concept_name


# In[107]:


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
    #print(tree.findall('results')[0].findall('result')[0].findall('metadata')[0].findall('entity'))#.findall('oaf:result')[0].findall('subject'))
	return subjects


# In[108]:


def get_openaire_subjects_from_title(title):
	title_words = title.split(' ')
	title_search_string = ""
	for word in title_words:
		word_clean = ''.join(x for x in word if x.isalpha())
		title_search_string += word_clean.lower() + ' '
	url = openaire_base_url+title_search_string
	#print(url)
	response = requests.get(url)
	if response.status_code == 200:
		openaire_subjects = get_openaire_subjects(response.text, title)
		return openaire_subjects
	else:
		return None


# In[109]:


def preprocess_term(term):
	# Split the term into words and filter out numeric-only words
	filtered_words = [word.lower() for word in term.split(' ') if not word.isnumeric()]
	# Rejoin the words to form the preprocessed term
	preprocessed_term = ' '.join(filtered_words)
	return preprocessed_term


# In[110]:

def fetch_openalex_works(concept_id, sort_by='cited_by_count:desc', per_page=200, max_pages=None):
    base_url = 'https://api.openalex.org/works'
    params = {
        'filter': f'concepts.id:{concept_id}',
        'sort': sort_by,
        'per_page': per_page,
    }
    page_count = 0

    while True:
        if max_pages is not None and page_count >= max_pages:
            break
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f'Failed to fetch data: {response.status_code}')
            break
        data = response.json()
        works = data.get('results', [])
        for work in works:
            print(work['id'])  # Or process the work object as needed
        cursor = data.get('meta', {}).get('next_cursor')
        if not cursor or cursor == '':
            break  # Exit loop if no more results
        params['cursor'] = cursor
        page_count += 1

def get_works_from_openalex(start_page=1, pages=100):
    
	concept_id = 'C154945302'
	sort_by = 'cited_by_count:desc'
	per_page = 200
	cursor = '*'
    
	base_url = 'https://api.openalex.org/works'
	params = {
        'filter': f'concepts.id:{concept_id}',
        'sort': sort_by,
        'per_page': per_page,
        'cursor': cursor,
	}
	page_count = 1
    
	while True:
		time.sleep(10)
		out_json = {}
		print(f'Fetching page: {page_count}')
		
  
		#url = openalex_works_api.replace('page=1', f'page={page}')
		response = requests.get(base_url, params=params)

		if response.status_code == 200:
			data = response.json()
			page_results = data['results']
			with open(f'data/raw_openalex_api_outputs/page_{page_count}.json', 'a+') as f:
				json.dump(data, f, indent=4)
			
			cnt = 0
			for work in page_results:
				cnt += 1
				print(f'Work count: {cnt}')
				if not work['title']:
					continue
				#print(work['title'])
				openalex_consepts = []
				for concept in work['concepts']:
					openalex_consepts.append(concept['display_name'])
				
	
				openaire_subjects = get_openaire_subjects_from_title(work['title'])
				
				if not openaire_subjects:
					continue
				if not openalex_consepts:
					continue
				out_json[work['title']] = {}
				#print(openalex_consepts)
				out_json[work['title']]['openalex'] = ' | '.join(openalex_consepts)
				#print(openaire_subjects)
				out_json[work['title']]['openaire'] = ' | '.join(openaire_subjects)
    
				matching = []
				similarities = []
				missmatches = []
				#print(out_json[work['title']]['openaire'])
				max_similarity = 0
				openaire_terms = out_json[work['title']]['openaire'].split(' | ')
				openalex_terms = out_json[work['title']]['openalex'].split(' | ')
				for openaire_term in openaire_terms:
					for openalex_term in openalex_terms:
						
						openaire_term = preprocess_term(openaire_term)
						openalex_term = preprocess_term(openalex_term)
						doc1 = nlp(openaire_term)
						doc2 = nlp(openalex_term)
						similarity = doc1.similarity(doc2)
						if similarity >= 1:
							matching.append({
								'openaire': openaire_term,
								'openalex': openalex_term,
								'similarity': similarity
							})
						elif similarity >= 0.8:
							similarities.append({
								'openaire': openaire_term,
								'openalex': openalex_term,
								'similarity': similarity
							})
						else:
							missmatches.append({
								'openaire': openaire_term,
								'openalex': openalex_term,
								'similarity': similarity
							})
				
				out_json[work['title']]['exact_matches'] = matching
				out_json[work['title']]['similarity'] = similarities
				out_json[work['title']]['missmatches'] = missmatches
		
			with open(f'data/output_{page_count}.json', 'a+') as f:  
				f.write(json.dumps(out_json, indent=4))

			cursor = data.get('meta', {}).get('next_cursor')	
			if not cursor or cursor == '':
				break  # Exit loop if no more results
			params['cursor'] = cursor
			page_count += 1
		else:
			print(f"Failed to fetch data: {response.status_code}")
			break


# In[111]:


get_works_from_openalex(51)

