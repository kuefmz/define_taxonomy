# Define a small taxonomy (~200 terms) for AI/ML domain


## Overview


The data folder is not complete as some of the sources are too large for GitHub

Collections that are considered:
- **OpenAlex**: data accessed on 14th February 2024
- **OpenAIRE**: data accessed on 15th February 2024


## Methodology

The methodology used can be seen on the image bellow


![methodology](./plots/methodology.png)


## Usage

Bellow you can find the commands that need to be run to get to execute the methodology.

### Step1
First we need to collect papers and their categories from OpenAlex and OpenAIRE and align them.

For this run the script 

```
python3 src/collect_initial_data.py
```


Some of the collected categories are noisy, this script also cleans that up.

### Step2

Ones the data is collected we need to look for the match for each category from each collection because we want to map them. The matches are selected based on their semantic similarity.

For this run the script.

```
python3 src/select_the_best_match_from_category_pairs.py
```

### Step3

Now that the papers with their mapped categories are ready and the category similarities, it is time to upload to a Neo4J database. This can take several days, depending on the machine that is used for the database and the amount of data collected.


```
python3 src/store_data_into_neo4j.py
```

### Step4

Ones the data is stored into the database we run a query to select all the category pairs and the supporting papers for both categories and their similarity.

```
python3 src/run_ne04j_query.py
```

### Step 5


Now that we have the pairs, we can run another script to transform the query results to a CSV and also calculate the missing 'Agreement' metric for the analysis.

```
python3 scr/transform_result_from_json_to_csv.py
```

### Step 6

This will generate the final data. The analysis is performed based on this data. The goal of this analysis is to produce a set of mapping alignments that can be aligned in the different knowledge graphs. 

### Step 7

The mapping produced in the previous steps should be manually validated.

Assuming that the generated mapping is stored in a CSV, the following scipt collects all the papers from the collected data that belong to both of the aligned categories.


```
python3 scr/validation.py
```

These papers should be manually validated by domain experts.



[![DOI](https://zenodo.org/badge/717105167.svg)](https://zenodo.org/doi/10.5281/zenodo.10987998)




