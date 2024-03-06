
import requests
import time
import json


base_url = "https://api.crossref.org/works"
max_retries = 20

def fetch_crossref_data(url, max_results=5):
    page = 0
    params = {
        "rows": max_results,
    }
    while True:
        try:
            retries = 0
            if page == 0:
                start = 0
            else:
                start = page*max_results+1

            print(f'Fetching page: {page}')
            params["offset"] = start
            response = requests.get(url, params=params)

            if response.status_code == 200:

                data = response.json()
                for item in data['message']['items']:

                    #parse id:
                    id = item.get('DOI')

                    # fetch year
                    year = item.get('published-print', {}).get('date-parts', [[""]])[0][0] if item.get('published-print') else ""

                    # fetch title
                    title = item.get('title')[0] if item.get('title') else ""

                    # fetch subjects
                    subjects = [subject for subject in item.get('subject', [])]

                    publication = {
                        'id': id,
                        'year': year,
                        'title': title,
                        'subjects': subjects,
                        'github_links': []
                    }

                    # fetch github links
                    if 'link' in item:
                        publication['github_links'] = [link['URL'] for link in item['link'] if 'github' in link['URL']]
                    with open('crossref_publications.jsonl', 'a+') as f:
                            f.write(json.dumps(publication) + '\n')

                page += 1
                time.sleep(1)

            else:
                print(f"Failed to fetch data: {response.status_code}")
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries > max_retries:
                print("Maximum retries reached, stopping...")
                break
            print(f"Request failed: {e}, retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    fetch_crossref_data(base_url, 1000)
