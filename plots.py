import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
min_samples = 5
df = pd.read_csv('output.csv')
df = df[(df['PapersInC1'] > min_samples) & (df['PapersInC1'] > min_samples)]

# Create a scatter plot
plt.figure(figsize=(20, 10))
plt.scatter(df['similarity'], df['Discripancy'])
plt.title('Scatter plot of Similarity vs. Discripancy')
plt.xlabel('Similarity')
plt.ylabel('Discripancy')
plt.grid(True)
plt.savefig(f'plots/similarity_and_agreement_cleaned_at_{min_samples}.png')

# Create a distribution plot for the calculated value in 20 buckets
# For elements with a similarity value of 1.0
df_similarity_1 = df[df['similarity'] == 1.0]
df_similarity_not_1 = df[df['similarity'] != 1.0]
counts, bins = np.histogram(df_similarity_1['Discripancy'], bins=np.linspace(0, 1, 21))
bin_centers = 0.5 * (bins[1:] + bins[:-1])

plt.figure(figsize=(10, 6))
plt.bar(bin_centers, counts, width=0.05)
plt.title('Distribution of Discripancies in Buckets (Similarity = 1.0)')
plt.xlabel('Discripancy Buckets')
plt.ylabel('Count')
plt.grid(True)
plt.savefig(f'plots/agreement_distplot_cleaned_at_{min_samples}.png')

filtered_df = df_similarity_1[(df_similarity_1['Discripancy'] > 0.4) & (df_similarity_1['similarity'] > 0.4)]
filtered_df.to_csv('filtered_output_sim_1_04_04.csv', index=False)


filtered_df = df_similarity_not_1[(df_similarity_not_1['Discripancy'] > 0.2) & (df_similarity_not_1['similarity'] > 0.2)]
filtered_df.to_csv('filtered_output_sim_not_1_02_02.csv', index=False)