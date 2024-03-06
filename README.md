# Define a small taxonomy (~200 terms) for AI/ML domain

The data folder is not complete as some of the sources are too large for GitHub

Collections that are considered:
- **OpenAlex**: data accessed on 14th November 2023
- **OpenAIRE**: data accessed on 15th November 2023
- **Arxiv**: data accessed on 15th of November 2023
- **CrossRef**: data accessed on 15th of November 2023

## Method/Usage

First we need to collect papers and their categories from OpenAlex and OpenAIRE and align them.

For this run the script 

"""
# Step1
python3 src/collect_initial_data.py
"""

Some of the collected categories are noisy, this script also cleans that up.

Ones the data is collected we need to look for the best match for each category from each collection because we want to map them

For this run the script:

"""
# Step2
python3 src/select_the_best_match_from_category_pairs.py
"""


To get all the best pair combinations run:

"""
# Step3.1

python3 src/get_all_the_pair_combinations.py
"""

