import json
import csv
import os
from collections import defaultdict

match_tuples = set([])
counts = {}



def process_matches(writer, matches):
    for _, match in matches.items():
        match_tuple = [match['openalex'], match['openaire']]
        match_string = '---'.join(match_tuple)
        #if match_string in counts.keys():
        #    counts[match_string] += 1
        #else:
        #    counts[match_string] = 1 
        #print(match_tuple)
        if match_string in match_tuples:
            #print('already exists')
            continue
        else:
            match_tuples.add(match_string)
        writer.writerow({
            'OpenAlex': match['openalex'],
            'OpenAIRE': match['openaire'],
            'Similarity': match['similarity'],
        })

# Function to process all JSON files and write the data to a CSV file
def process_json_folder_to_csv(folder_path, output_csv_path):
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['OpenAlex', 'OpenAIRE', 'Similarity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for file_name in os.listdir(folder_path):
            print(file_name)
            if file_name.endswith('.json'):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    for title, details in data.items():
                        #for cat in data[title]['openaire']:
                        #    cat_str = 'openaire---'+cat
                        #    if cat_str in counts.keys():
                        #        counts[cat_str] += 1
                        #    else:
                        #        counts[cat_str] = 1
                        #for cat in data[title]['openalex']:
                        #    cat_str = 'openalex---'+cat
                        #    if cat_str in counts.keys():
                        #        counts[cat_str] += 1
                        #    else:
                        #        counts[cat_str] = 1
                        process_matches(writer, details['best_matches_openalex'])
                        process_matches(writer, details['best_matches_openaire'])

process_json_folder_to_csv('data/papers_with_openalex_and_openaire_categories_aligned', 'data/cat_pairs.csv')