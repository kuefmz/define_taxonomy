import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv('output.csv')

# Create a scatter plot
plt.figure(figsize=(20, 10))
plt.scatter(df['similarity'], df['Discripancy'])
plt.title('Scatter plot of Similarity vs. Discripancy')
plt.xlabel('Similarity')
plt.ylabel('Discripancy')
plt.grid(True)
plt.show()

# Create a distribution plot for the calculated value in 20 buckets
# For elements with a similarity value of 1.0
df_similarity_1 = df[df['similarity'] == 1.0]
counts, bins = np.histogram(df_similarity_1['Discripancy'], bins=np.linspace(0, 1, 21))
bin_centers = 0.5 * (bins[1:] + bins[:-1])

plt.figure(figsize=(10, 6))
plt.bar(bin_centers, counts, width=0.05)
plt.title('Distribution of Discipancies in Buckets (Similarity = 1.0)')
plt.xlabel('Discipancy Buckets')
plt.ylabel('Count')
plt.grid(True)
plt.show()
