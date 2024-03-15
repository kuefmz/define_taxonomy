import json
import csv

# Function to calculate the new column value
def calculate_value(papers_in_both, papers_in_c1, papers_in_c2):
    return papers_in_both / (papers_in_c1 + papers_in_c2 - papers_in_both)

# Define the CSV file where the transformed data will be saved
with open('output.csv', mode='r') as infile, open('output_with_agreement.csv', mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Read the header row and write it to the output file, appending 'New Value' as a new header
    headers = next(reader)
    writer.writerow(headers + ['Agreement'])

    for row in reader:
        print(row)
        # Perform your calculation here; this example doubles the value in the first column
        agreement = calculate_value(int(row[-1]), int(row[-2]), int(row[-3]))

        # Write the original row with the new value appended to the output CSV
        writer.writerow(row + [agreement])


        