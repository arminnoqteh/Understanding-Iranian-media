from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from hazm import SentenceTokenizer, WordTokenizer, POSTagger, Lemmatizer
from hazm.utils import stopwords_list

word_tokenize = WordTokenizer().tokenize
sent_tokenize = SentenceTokenizer().tokenize
lemmatizer = Lemmatizer()
pos_tag = POSTagger('hazm_models/pos_tagger.model')

from tqdm import tqdm

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return 'a'
    elif tag.startswith('V'):
        return 'v'
    elif tag.startswith('N'):
        return 'n'
    elif tag.startswith('R'):
        return 'r'
    else:
        return 'n'
    
    from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import Parallel, delayed
from collections import Counter
import dill
from multiprocessing import Pool

def extract_keywords(texts, num_keywords):
# Preprocess with progress bar without any multiprocessing, just give me a break!
    preprocessed_texts = Parallel(n_jobs=-1, backend='threading')(delayed(preprocess_text)(text) for text in tqdm(texts))

    # Combine all texts into one
    combined_text = ' '.join(preprocessed_texts)

    vectorizer = TfidfVectorizer(stop_words=stopwords_list())
    tfidf_matrix = vectorizer.fit_transform([combined_text])
    feature_names = vectorizer.get_feature_names_out()

    feature_index = tfidf_matrix.nonzero()[1]
    tfidf_scores = zip(feature_index, [tfidf_matrix[0, x] for x in feature_index])
    features_scores = [(feature_names[i], s) for (i, s) in tfidf_scores]
    sorted_scores = sorted(features_scores, key=lambda x: x[1], reverse=True)

    return [word for word,_ in sorted_scores[:num_keywords]]


def preprocess_text(text):
    sentences = sent_tokenize(text)
    lemmatized_words = []
    for sentence in sentences:
        words = word_tokenize(sentence)
        lemmas = [lemmatizer.lemmatize(word) for word in words]
        pos_tags = pos_tag.tag(lemmas)
        lemmatized_words.extend([lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags])

    return ' '.join(lemmatized_words)
