#!/usr/bin/env python
# coding: utf-8

import requests
import time
import json


max_retries = 20
base_url = 'http://api.openaire.eu/search/publications'
# Total number of publications: 179174368

def get_publications_topics():
    params = {
        'format': 'json',
        'size': 500,
    }
    page = 21
    cursor = '*'

    with open('publications_per_page/publications_cursor.jsonl', 'a+') as file:
        while True:
            try:
                publication_json = {
                    "id": "",
                    "title": "",
                    "year": "",
                    "source": [],
                    "subjects": [],
                }
                retries = 0
                print(f'Fetching page: {page}')

                #params['page'] = page
                params['cursor'] = cursor
                response = requests.get(base_url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    file.write(json.dumps(data) + '\n')

                    for publication in data['response']['results']['result']:
                        #parse id
                        publication_json["id"] = publication["header"]["dri:objIdentifier"]["$"]

                        publication = publication["metadata"]["oaf:entity"]["oaf:result"]

                        #parse title
                        if "title" in publication.keys():
                            if type(publication["title"]) == list:
                                for title in publication["title"]:
                                    if title["@classname"] == "main title":
                                        publication_json["title"] = title["$"]
                            else:
                                publication_json["title"] = publication["title"]["$"]

                        #print(f"Processing prublication with title: {publication_json['title']}")
                        #parse year
                        if "dateofacceptance" in publication.keys():
                            publication_json["year"] = publication["dateofacceptance"]["$"].split('-')[0]

                        #parse source
                        #if "source" in publication.keys():
                        #    if type(publication["source"]) == list:
                        #        for source in publication['source']:
                        #            if source:
                        #                publication_json["source"].append(source["$"])
                        #    else:
                        #        publication_json["source"].append(publication["source"]["$"])

                        #parse subjects
                        if "subject" in publication.keys():
                            if type(publication["subject"]) == list:
                                for subject in publication['subject']:
                                    publication_json["subjects"].append(subject["$"])
                            else:
                                publication_json["subjects"].append(publication["subject"]["$"])


                        with open('openaire_publications_cursor.jsonl', 'a+') as f:
                            f.write(json.dumps(publication_json) + '\n')

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
                print(f"Request failed: {e}, retrying...")
                time.sleep(5)  # Wait before retrying


if __name__ == "__main__":
    get_publications_topics()


