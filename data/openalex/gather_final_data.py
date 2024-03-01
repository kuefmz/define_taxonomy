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
	cursor = "IlszNDgsIDEwMC4wLCAzNDgsICdodHRwczovL29wZW5hbGV4Lm9yZy9XMjEzNzc0MzE4MCddIg=="
    
	base_url = 'https://api.openalex.org/works'
	params = {
        'filter': f'concepts.id:{concept_id}',
        'sort': sort_by,
        'per_page': per_page,
        'cursor': cursor,
	}
	page_count = 224
    
	while True:
		time.sleep(10)
		out_json = {}
		print(f'Fetching page: {page_count}')
		
  
		#url = openalex_works_api.replace('page=1', f'page={page}')
		respon