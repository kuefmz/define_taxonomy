import os
import json
import pandas as pd


df = pd.read_csv('data/supports.csv')
df.drop('PairSupport', axis=1, inplace=True)

def update_df_from_json(folder_path, df, reverse=False):
    file_names = os.listdir(folder_path)
    file_names.sort(reverse=reverse)
    updated_csv_path = 'data/updated.csv'
    for file_name in file_names:
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                data = json.load(file)
                for title, details in data.items():
                    print(title)
                    #update just openaire
                    for cat_openaire in details['openaire']:
                        for index, row in df[df['OpenAIRE'] == cat_openaire].iterrows():
                            df.at[index, 'SupportOpenAIRE'] += 1
                    # update just openalex
                    for cat_openalex in details['openalex']:
                        for index, row in df[df['OpenAlex'] == cat_openalex].iterrows():
                            df.at[index, 'SupportOpenAlex'] += 1
                    #update the overlap
                    for cat_openaire in details['openaire']:
                        for cat_openalex in details['openalex']:
                            for index, row in df[(df['OpenAIRE'] == cat_openaire) & (df['OpenAlex'] == cat_openalex)].iterrows():
                                df.at[index, 'Overlap'] += 1
                    
                    with open('data/processed_pages_papers.txt', 'a') as file:
                        file.write(title + '\n')
            print('Calculation_done, saving the results')
            df.to_csv(updated_csv_path, index=False)
            with open('data/preprocessed_files.txt', 'a') as file:
                        file.write(file_name + '\n')
    
# Example usage
folder_path = 'data/papers_with_openalex_and_openaire_categories_aligned'
update_df_from_json(folder_path, df)

# Save the updated DataFrame to a new CSV
updated_csv_path = 'data/updated.csv'
df.to_csv(updated_csv_path, index=False)