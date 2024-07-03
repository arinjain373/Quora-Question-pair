import re
from bs4 import BeautifulSoup
import distance
import pickle
import numpy as np
import zipfile

import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

zip_file_path = 'cv.zip'
cv_file_name = 'cv.pkl'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    if cv_file_name in zip_ref.namelist():
        zip_ref.extract(cv_file_name)

with open(cv_file_name, 'rb') as file:
    cv = pickle.load(file)


def test_common_words(q1, q2):
    w1 = set(map(lambda word: word.lower().strip(), q1.split(" ")))
    w2 = set(map(lambda word: word.lower().strip(), q2.split(" ")))
    return len(w1 & w2)


def test_total_words(q1, q2):
    w1 = set(map(lambda word: word.lower().strip(), q1.split(" ")))
    w2 = set(map(lambda word: word.lower().strip(), q2.split(" ")))
    return len(w1) + len(w2)


def apply_stemming_and_lemmatization(sentence):
    words = word_tokenize(sentence)
    modified_words = [stemmer.stem(lemmatizer.lemmatize(word)) for word in words]
    return ' '.join(modified_words)


def test_fetch_token_features(q1, q2):
    SAFE_DIV = 0.0001
    STOP_WORDS = stopwords.words("english")
    token_features = [0.0] * 8

    q1_tokens = q1.split()
    q2_tokens = q2.split()

    if len(q1_tokens) == 0 or len(q2_tokens) == 0:
        return token_features

    q1_words = set([word for word in q1_tokens if word not in STOP_WORDS])
    q2_words = set([word for word in q2_tokens if word not in STOP_WORDS])

    q1_stops = set([word for word in q1_tokens if word in STOP_WORDS])
    q2_stops = set([word for word in q2_tokens if word in STOP_WORDS])

    common_word_count = len(q1_words.intersection(q2_words))
    common_stop_count = len(q1_stops.intersection(q2_stops))
    common_token_count = len(set(q1_tokens).intersection(set(q2_tokens)))

    token_features[0] = common_word_count / (min(len(q1_words), len(q2_words)) + SAFE_DIV)
    token_features[1] = common_word_count / (max(len(q1_words), len(q2_words)) + SAFE_DIV)
    token_features[2] = common_stop_count / (min(len(q1_stops), len(q2_stops)) + SAFE_DIV)
    token_features[3] = common_stop_count / (max(len(q1_stops), len(q2_stops)) + SAFE_DIV)
    token_features[4] = common_token_count / (min(len(q1_tokens), len(q2_tokens)) + SAFE_DIV)
    token_features[5] = common_token_count / (max(len(q1_tokens), len(q2_tokens)) + SAFE_DIV)
    token_features[6] = int(q1_tokens[-1] == q2_tokens[-1])
    token_features[7] = int(q1_tokens[0] == q2_tokens[0])

    return token_features


def test_fetch_length_features(q1, q2):
    length_features = [0.0] * 3

    q1_tokens = q1.split()
    q2_tokens = q2.split()

    if len(q1_tokens) == 0 or len(q2_tokens) == 0:
        return length_features

    length_features[0] = abs(len(q1_tokens) - len(q2_tokens))
    length_features[1] = (len(q1_tokens) + len(q2_tokens)) / 2
    strs = list(distance.lcsubstrings(q1, q2))
    length_features[2] = len(strs[0]) / (min(len(q1), len(q2)) + 1)

    return length_features


def preprocess(q):
    q = str(q).lower().strip()
    q = q.replace('%', ' percent')
    q = q.replace('$', ' dollar ')
    q = q.replace('₹', ' rupee ')
    q = q.replace('€', ' euro ')
    q = q.replace('@', ' at ')

    contractions = {
        "ain't": "am not", "aren't": "are not", "can't": "can not", "can't've": "can not have", "'cause": "because",
        "could've": "could have", "couldn't": "could not", "couldn't've": "could not have", "didn't": "did not",
        "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hadn't've": "had not have", "hasn't": "has not",
        "haven't": "have not", "he'd": "he would", "he'd've": "he would have", "he'll": "he will", "he'll've": "he will have",
        "he's": "he is", "how'd": "how did", "how'd'y": "how do you", "how'll": "how will", "how's": "how is",
        "i'd": "i would", "i'd've": "i would have", "i'll": "i will", "i'll've": "i will have", "i'm": "i am",
        "i've": "i have", "isn't": "is not", "it'd": "it would", "it'd've": "it would have", "it'll": "it will",
        "it'll've": "it will have", "it's": "it is", "let's": "let us", "ma'am": "madam", "mayn't": "may not",
        "might've": "might have", "mightn't": "might not", "mightn't've": "might not have", "must've": "must have",
        "mustn't": "must not", "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have",
        "o'clock": "of the clock", "oughtn't": "ought not", "oughtn't've": "ought not have", "shan't": "shall not",
        "sha'n't": "shall not", "shan't've": "shall not have", "she'd": "she would", "she'd've": "she would have",
        "she'll": "she will", "she'll've": "she will have", "she's": "she is", "should've": "should have",
        "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have", "so's": "so as",
        "that'd": "that would", "that'd've": "that would have", "that's": "that is", "there'd": "there would",
        "there'd've": "there would have", "there's": "there is", "they'd": "they would", "they'd've": "they would have",
        "they'll": "they will", "they'll've": "they will have", "they're": "they are", "they've": "they have",
        "to've": "to have", "wasn't": "was not", "we'd": "we would", "we'd've": "we would have", "we'll": "we will",
        "we'll've": "we will have", "we're": "we are", "we've": "we have", "weren't": "were not", "what'll": "what will",
        "what'll've": "what will have", "what're": "what are", "what's": "what is", "what've": "what have",
        "when's": "when is", "when've": "when have", "where'd": "where did", "where's": "where is", "where've": "where have",
        "who'll": "who will", "who'll've": "who will have", "who's": "who is", "who've": "who have", "why's": "why is",
        "why've": "why have", "will've": "will have", "won't": "will not", "won't've": "will not have", "would've": "would have",
        "wouldn't": "would not", "wouldn't've": "would not have", "y'all": "you all", "y'all'd": "you all would",
        "y'all'd've": "you all would have", "y'all're": "you all are", "y'all've": "you all have", "you'd": "you would",
        "you'd've": "you would have", "you'll": "you will", "you'll've": "you will have", "you're": "you are",
        "you've": "you have"
    }

    q_decontracted = [contractions[word] if word in contractions else word for word in q.split()]
    q = ' '.join(q_decontracted)

    q = BeautifulSoup(q, "html.parser").get_text()
    q = re.sub(r'\W', ' ', q).strip()

    return q


def query_point_creator(q1, q2):
    input_query = []

    q1 = preprocess(q1)
    q2 = preprocess(q2)
    q1 = apply_stemming_and_lemmatization(q1)
    q2 = apply_stemming_and_lemmatization(q2)

    input_query.append(len(q1))
    input_query.append(len(q2))
    input_query.append(len(q1.split(" ")))
    input_query.append(len(q2.split(" ")))
    input_query.append(test_common_words(q1, q2))
    input_query.append(test_total_words(q1, q2))
    input_query.append(round(test_common_words(q1, q2) / test_total_words(q1, q2), 2))

    token_features = test_fetch_token_features(q1, q2)
    input_query.extend(token_features)

    length_features = test_fetch_length_features(q1, q2)
    input_query.extend(length_features)

    print(f"Input query shape: {np.array(input_query).shape}")

    q1_bow = cv.transform([q1]).toarray()
    q2_bow = cv.transform([q2]).toarray()

    print(f"q1_bow shape: {q1_bow.shape}")
    print(f"q2_bow shape: {q2_bow.shape}")

    return np.hstack((np.array(input_query).reshape(1, -1), q1_bow, q2_bow))
