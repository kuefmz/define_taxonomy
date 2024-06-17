import os
import re

def find_missing_indices(folder_path, output_file):
    # Regular expression to match filenames of the form 'page_{ind}.json'
    pattern = re.compile(r'page_(\d+)\.json')
    
    # List to store all the indices
    indices = []
    
    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match:
            # Extract the index and convert to integer
            indices.append(int(match.group(1)))
    
    if not indices:
        print("No files matching the pattern were found.")
        return
    
    # Find the minimum and maximum indices
    min_index = min(indices)
    max_index = max(indices)
    
    # Generate a set of all possible indices in the range
    all_indices = set(range(min_index, max_index + 1))
    
    # Find the missing indices
    missing_indices = sorted(all_indices - set(indices))
    
    # Write the missing indices to the output file
    with open(output_file, 'w') as f:
        for index in missing_indices:
            f.write(f"{index}\n")
    
    print(f"Missing indices written to {output_file}")

# Example usage:
folder_path = '/home/jenifer/define_taxonomy/data/raw_openalex_api_outputs/'
output_file = 'missing_indices.txt'
find_missing_indices(folder_path, output_file)
