from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer
from hazm import Normalizer, word_tokenize, SentEmbedding
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA

df = pd.read_csv('data/tasnim.csv').dropna().sample(25, random_state=42)

# Load the sentence transformer model
sent2vec_model = (
        SentEmbedding("hazm_models/sent2vec/sent2vec-naab.model")
    )
# Normalize and tokenize the text
normalizer = Normalizer()
# stopwords = stopword_list()

def preprocess_text(text):
    # Check if the text is string
    # if isinstance(text, str):
    return normalizer.normalize(text)
    # else:
        # return ""

labels= ['سیاسی','اجتماعی','اقتصادی']
label_embeddings = [sent2vec_model[label] for label in labels]

# Preprocess the text and generate embeddings
texts = [preprocess_text(text) for text in df['body']]
embeddings = [sent2vec_model[text] for text in texts]


silhouette_scores = []
for n_clusters in range(2, 11):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(embeddings)
    silhouette_scores.append(silhouette_score(embeddings, kmeans.labels_))

optimal_n_clusters = silhouette_scores.index(max(silhouette_scores)) + 2
print(f'Optimal number of clusters: {optimal_n_clusters}')
# optimal_n_clusters = 4
optimal_kmeans = KMeans(n_clusters=optimal_n_clusters, random_state=42)
optimal_kmeans.fit(embeddings)

# Extract each clusters' keywords using embedRank
df['cluster'] = optimal_kmeans.labels_
keywords = []
df.groupby('cluster').apply(lambda x: keywords.append(embedRank(' '.join(x['body']), 5)))
df.to_csv('data/tasnim_keywords.csv', index=False)


import matplotlib.pyplot as plt

# Visualize each cluster and display keywords
# Perform dimension reduction using PCA
pca = PCA(n_components=2)
reduced_embeddings = pca.fit_transform(embeddings)

for cluster_id in range(optimal_n_clusters):
    cluster_embeddings = [embedding for i, embedding in enumerate(reduced_embeddings) if optimal_kmeans.labels_[i] == cluster_id]
    plt.scatter(*zip(*cluster_embeddings), label=f'Cluster {cluster_id}')
    
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Cluster Visualization')
plt.legend()
plt.show()









# # Measure similarity and assign labels
# def assign_label(embedding):
#     return cosine_similarity([embedding], label_embeddings)

# results = [assign_label(embedding) for embedding in embeddings]
# print(results)
