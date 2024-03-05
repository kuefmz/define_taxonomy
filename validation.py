import json
import os
import pandas as pd
import json


def select_pairs_with_high_agreement(df):
    selected_tuples = []
    filtered_df = df[df['Agreement'] > 0.5]
    
    for index, row in filtered_df.iterrows():
        if row['Source1'] == 'OpenAlex':
            category_tuple = (row['Category1'], row['Category2'])
        elif row['Source2'] == 'OpenAlex':
            category_tuple = (row['Category2'], row['Category1'])
        else:
            continue
        
        if category_tuple not in selected_tuples:
            selected_tuples.append(category_tuple)
        if len(selected_tuples) == 100:
            break
    
    return selected_tuples


def preprocess_term_new(term):
    terms = term.split(' ').split('.').split('/').split(',')
    for i in range(len(terms)):
        terms[i] = terms[i].replace('[', ' ').replace(']', ' ').replace('"', ' ').replace('&', ' ')
        terms[i] = ''.join(c for c in terms[i] if not c.isdigit())
    filtered_words = [word.lower() for word in terms if not word.isnumeric()]
    preprocessed_term = ' '.join(filtered_words)
    return preprocessed_term


def preprocess_term(term):
        filtered_words = [word.lower() for word in term.split(' ') if not word.isnumeric()]
        preprocessed_term = ' '.join(filtered_words)
        return preprocessed_term


def main():
    df = pd.read_csv('filtered_output_sim_not_1_04_04.csv')
    selected_pairs = select_pairs_with_high_agreement(df)
    #print(selected_pairs)
    #print(len(selected_pairs))
    json_folder_path = 'data/openalex_openaire/data'
    
    selected_papirs_to_validate = {}
    for pair in selected_pairs:
        selected_papirs_to_validate[pair] = []
    for filename in os.listdir(json_folder_path):
        print(f'Processing file: {filename}')
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_folder_path, filename)
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                for title, details in data.items():
                    categories_openalex = details['openalex'].split(" | ")
                    categories_openaire = details['openaire'].split(" | ")
                    categories_openalex = [preprocess_term(x) for x in categories_openalex]
                    categories_openaire = [preprocess_term(x) for x in categories_openaire]
                    for pair in selected_pairs:
                        if pair[0] in categories_openalex and pair[1] in categories_openaire:
                            selected_papirs_to_validate[pair].append(title)
    
    converted_dict = {str(key): value for key, value in selected_papirs_to_validate.items()}
    with open('papers_to_validate.json', 'w') as json_file:
        json.dump(converted_dict, json_file, indent=4)		


if __name__ == "__main__":
    main()