from hazm import stopwords_list, Normalizer, Lemmatizer, word_tokenize

class Preprocessor:
    def __init__(self):
        self.normalizer = Normalizer()
        self.lemmatizer = Lemmatizer()
        self.stopwords = stopwords_list()
        
    def preprocess(self, text):
        # Normalize the text
        normalized_text = self.normalizer.normalize(text)
        
        # Tokenize the text into words
        tokens = word_tokenize(normalized_text)
        
        # Remove stopwords
        tokens = [token for token in tokens if token not in self.stopwords]
        
        # Lemmatize the words
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
                
        # Join the tokens back into a preprocessed text
        preprocessed_text = ' '.join(lemmatized_tokens)
        
        return preprocessed_text