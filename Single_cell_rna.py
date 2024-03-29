# -*- coding: utf-8 -*-
"""Single-Cell-RNA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/184GxPOaSW7TcNE4MiJcEkoJ2LsUNoxQu
"""

#Import Libraries
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.impute import SimpleImputer
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns


#Load the data
def load_data(filepath):
    # Load the data using chunking
    chunks = pd.read_csv(filepath, chunksize=1000)  # Adjust chunk size as needed
    data = pd.concat(chunks, ignore_index=True)
    return data

#Normalize the loaded data
def normalize_data(data):
    numeric_data = data.select_dtypes(include=[np.number])
    total_counts_per_cell = numeric_data.sum(axis=1)
    scaling_factor = total_counts_per_cell / 1e6
    data_normalized = (numeric_data.div(scaling_factor, axis=0)) * 1e6
    return data_normalized

#Filepath by downloading it or through drive
filepath = '/content/drive/MyDrive/Colab/File.csv'

data = load_data(filepath)

data_normalized = normalize_data(data)

perplexity_value = 5 #Can be changed based on the dataset

#Function to reduce dimensionality of the the large dataset using PCA and TSNE
def reduce_dimension(data1, n_components):
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(data1.transpose())
    tsne = TSNE(n_components=2, random_state=0, perplexity=perplexity_value)
    tsne_result = tsne.fit_transform(pca_result)
    return tsne_result

#Function to perform Clustering on the reduced dataset from above using K-Means
def perform_clustering(data2, n_clusters, n_init):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=n_init).fit(data2)
    return kmeans

# Handle missing values using Imputation(Filling None values)
imputer = SimpleImputer(strategy='mean')
data_imputed = pd.DataFrame(imputer.fit_transform(data_normalized), columns=data_normalized.columns, index=data_normalized.index)

reduced_data = reduce_dimension(data_imputed, 6)

kmeans_model = perform_clustering(reduced_data, 6, 10)
cluster_labels = kmeans_model.labels_

#Function to find the best two clusters from above to perform Differential Analysis on
def select_top_clusters(cluster_labels, num_clusters=2):
    cluster_counts = np.bincount(cluster_labels)
    top_cluster_indices = np.argsort(cluster_counts)[-num_clusters:][::-1]
    top_clusters = [i for i in top_cluster_indices if cluster_counts[i] > 0]
    return top_clusters

select_top_clusters(cluster_labels,2)

#Differential Analysis is performed on the normalized data based on the cluster labels from above
def differential_expression(data3, cluster_labels):
    data3 = np.log1p(data3)
    cluster0_cells = data3.columns[cluster_labels == 6]
    cluster1_cells = data3.columns[cluster_labels == 4]
    casedata = data3[cluster1_cells]
    controldata = data3[cluster0_cells]
    ttest_results = stats.ttest_ind(data3[cluster0_cells], data3[cluster1_cells], axis=1)
    significant_genes = data3.index[ttest_results.pvalue < 0.05]
    significant_gene_and_expression = data3.loc[significant_genes, :]
    return significant_gene_and_expression

deg_data = differential_expression(data_normalized, cluster_labels)

#Visualizations
#Clusters
sns.scatterplot(x=reduced_data[:, 0], y=reduced_data[:, 1], hue=kmeans_model.labels_, palette='viridis')
plt.title('t-SNE Visualization of Clusters')
plt.xlabel('t-SNE Component 1')
plt.ylabel('t-SNE Component 2')
plt.show()

#Differential Analysis data Box-Plot
plt.figure(figsize=(12, 6))
sns.boxplot(data=deg_data)
plt.title(f'Expression of Significant Genes - Plot')
plt.xlabel('Genes')
plt.ylabel('Expression (Log-scale)')
plt.xticks(rotation=90)
plt.show()
