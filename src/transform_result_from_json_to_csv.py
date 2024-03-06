import json
import csv

# Function to calculate the new column value
def calculate_value(papers_in_both, papers_in_c1, papers_in_c2):
    return papers_in_both / (papers_in_c1 + papers_in_c2 - papers_in_both)

# Load the JSON data
with open('similarity_support.json', 'r', encoding="utf-8-sig") as file:
    data = json.load(file)

# Define the CSV file where the transformed data will be saved
with open('output.csv', 'w', newline='') as csvfile:
    fieldnames = ['Category1', 'Source1', 'Category2', 'Source2', 'similarity', 'PapersInC1', 'PapersInC2', 'PapersInBoth', 'Discripancy']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    # Process each item in the JSON file
    for item in data:
        calculated_value = calculate_value(item['PapersInBoth'], item['PapersInC1'], item['PapersInC2'])
        # Add the calculated value to the item
        item['Discripancy'] = calculated_value
        # Write the item to the CSV file
        writer.writerow(item)