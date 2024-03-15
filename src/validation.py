import json
import os
import pandas as pd
import json
from utils.utils import preprocess_term



def select_pairs_with_high_agreement(df):
    selected_tuples = []
    #filtered_df = df[df['Agreement'] > 0.5]
    #filtered_df = df[df['Similarity'] >= 1.0]
    #filtered_df.to_csv('exact_matches.csv', index=False)
    filtered_df = df
    
    for index, row in filtered_df.iterrows():
        if row['Source1'] == 'OpenAlex':
            category_tuple = (row['Category1'], row['Category2'])
        elif row['Source2'] == 'OpenAlex':
            category_tuple = (row['Category2'], row['Category1'])
        else:
            continue
        
        if category_tuple not in selected_tuples:
            selected_tuples.append(category_tuple)
        #if len(selected_tuples) == 100:
        #    break
    
    return selected_tuples


def main():
    df = pd.read_csv('data/matching_summaries/filtered_output_sim_not_1_05_-1.csv')
    selected_pairs = select_pairs_with_high_agreement(df)
    print(len(selected_pairs))
    json_folder_path = 'data/remove_underrepresented_categories'
    
    selected_papirs_to_validate = {}
    print(selected_pairs)
    for pair in selected_pairs:
        selected_papirs_to_validate[pair] = []
    for filename in os.listdir(json_folder_path):
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_folder_path, filename)
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                for title, details in data.items():
                    categories_openalex = details['openalex']
                    categories_openaire = details['openaire']
                    for pair in selected_pairs:
                        if pair[0] in categories_openalex and pair[1] in categories_openaire:
                            selected_papirs_to_validate[pair].append(title)
    
    converted_dict = {str(key): value for key, value in selected_papirs_to_validate.items()}
    with open('papers_to_validate_05.json', 'w') as json_file:
        json.dump(converted_dict, json_file, indent=4)		


if __name__ == "__main__":
    main()