#!/usr/bin/env python
# coding: utf-8

import requests
import json
from math import ceil
import time


openalex_url = "https://api.openalex.org/works"
concepts_url = "https://api.openalex.org/concepts"

metadata = {
    "count": 65073,
    "db_response_time_ms": 48,
    "page": 1,
    "per_page": 25,
    "groups_count": None
}
pages = ceil(metadata['count']/metadata['per_page'])
max_retries = 25


def download_ai_ml_articles(url):
    params = {}

    articles = []

    page = 1

    while True:
        params['page'] = page
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            #print(data['results'])
            #print(data['results'][0]['authorships']['keywords'])
            #print(data['results'][0]['concepts'])
            articles.extend(data['results'])

            page += 1
            print(page)
            if page >= 10:
                with open('openalex_articles.jsonl', 'a+') as f:
                    print('Written')
                    f.write(json.dumps(articles) + '\n')
                break
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break


def download_concepts(url):
    params = {"per_page": 200}

    page = 0
    cursor = '*'
    with open('concepts_per_page/concepts_cursor.jsonl', 'a+') as file:
        while True:
            try:
                retries = 0
                print(f'Fetching page: {page}')

                #params['page'] = page
                params['cursor'] = cursor
                response = requests.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    page_results = data['results']
                    #file.write(json.dumps(page_results) + '\n')

                    for concept in page_results:
                        print(f"Building up concept: {concept['display_name']}")
                        concept_json = {
                            "id": concept["id"],
                            "name": concept['display_name'],
                            "ancestors": [],
                            "related_concepts": [],
                            "counts_by_year": concept['counts_by_year'],
                        }

                        for ancestor in concept['ancestors']:
                            concept_json['ancestors'].append(ancestor['display_name'])
                        for related_concept in concept['related_concepts']:
                            concept_json['related_concepts'].append(related_concept['display_name'])

                        #with open('openalex_concepts_cursor.jsonl', 'a+') as f:
                        #    f.write(json.dumps(concept_json) + '\n')
                        with open(f'concepts_per_page/concepts_cursor_{page}.jsonl', 'a+') as file:
                            file.write(json.dumps(concept_json))

                    page += 1
                    cursor = data['meta']['next_cursor']
                    if not cursor:
                        break
                    time.sleep(1)
                else:
                    print(f"Failed to fetch data: {response.status_code}")
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > max_retries:
                    print("Maximum retries reached, stopping...")
                    break
                print(f"Request failed: {e}, retrying in 5 seconds...")
                time.sleep(5)  # Wait for 5 seconds before retrying

if __name__ == "__main__":
    download_concepts(concepts_url)

