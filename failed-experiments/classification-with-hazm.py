from hazm import SentEmbedding
from hazm import POSTagger
from hazm.corpus_readers import PersicaReader
from hazm import Normalizer
from hazm import word_tokenize
from hazm import sent_tokenize
from tqdm import tqdm

import pandas as pd
import concurrent
from ast import literal_eval

normalizer = Normalizer()
model = (SentEmbedding("hazm_models/sent2vec/sent2vec-naab.model"))
# Demonstration for embedding a sentence
# sent2vec_model["سلام"]

# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

import concurrent.futures
from tqdm import tqdm
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def embed_sentence(sentence):
    try:
        return model[normalizer.normalize(sentence)]
    except Exception as e:
        print(f"Error embedding sentence: {sentence}")
        print(f"Error message: {str(e)}")
        return None
    
def embed_df_multiprocessing(df, column):
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use list comprehension to create a list of futures
        futures = [executor.submit(embed_sentence, sentence) for sentence in df[column]]

        # Use tqdm for progress bar, concurrent.futures.as_completed for concurrency
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            # Get the result from the future
            result = future.result()

    # Add the embedded sentences as a new column to the dataframe
    df['embedded_sentences'] = [future.result() for future in futures]

    return df

def embed_array_multiprocessing(sentences):
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use list comprehension to create a list of futures
        futures = [executor.submit(embed_sentence, sentence) for sentence in sentences]

        # Use tqdm for progress bar, concurrent.futures.as_completed for concurrency
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            # Get the result from the future
            result = future.result()

    # Add the embedded sentences as a new column to the dataframe
    return [future.result() for future in futures]

def classify(embedded_labels, embedded_text):

    scores = []
    embedded_text = embedded_text.reshape(1, -1)
    for embedded_label in embedded_labels:
        # Reshape embedded label to match the shape of embedded text
        embedded_label = embedded_label.reshape(1, -1) 
        
        # Calculate cosine similarity between embedded label and embedded text
        similarity_score = cosine_similarity(embedded_label, embedded_text)
        scores.append(similarity_score)

    # Convert scores to probabilities
    probabilities = softmax(scores)
    highest_index = np.argmax(probabilities, axis=0)
    # flatten and fix probabilities
    return probabilities.flatten(), highest_index.item()

def softmax(scores):
    # Apply softmax function to convert scores to probabilities
    exp_scores = np.exp(scores)
    probabilities = exp_scores / np.sum(exp_scores, axis=0)

    return probabilities

def classify_df(df, labels):
    embedded_labels = embed_array_multiprocessing(labels)
    embedded_texts = embed_array_multiprocessing(df['abstract'])
    probabilties = []
    chosen_labels = []
    for text in embedded_texts:
        scores, highestindex = classify(embedded_labels, text)
        probabilties.append(scores)
        chosen_labels.append(labels[highestindex])

    df['probabilties'] = probabilties
    df['chosen_labels'] = chosen_labels
    return df


# import pandas as pd
# df = pd.read_csv('data/khabaronline-embedded.csv').sample(5)
# services = ['سیاسی','اقتصادی','اجتماعی']
# services_embeddings = embed_array_multiprocessing(services)
# probabilties, highestindex = classify(services_embeddings, embed_sentence(df['body'].iloc[0]))
# print(probabilties)
# print(services[highestindex.item()])
# df = classify_df(df,services)
# print(df[['service','chosen_labels','probabilties']])