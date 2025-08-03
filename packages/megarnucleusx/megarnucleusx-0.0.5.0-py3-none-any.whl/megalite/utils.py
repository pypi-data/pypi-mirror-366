try:
    import numpy as np
    import nltk
except ImportError:
    np = None
    nltk = None

def simple_mean(values):
    if np:
        return np.mean(values)
    return sum(values) / len(values)

def tokenize(text):
    if nltk:
        return nltk.word_tokenize(text)
    return text.split()
