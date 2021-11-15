# from gensim.utils import tokenize
import numpy as np
import jieba.posseg as pseg
import codecs
from rank_bm25 import BM25Okapi
# from gensim import corpora
# from gensim.summarization import bm25
import os
import re

stop_words = './asset/stopwords.txt'
stopwords = codecs.open(stop_words, 'r', encoding='utf8').readlines()
stopwords = [w.strip() for w in stopwords]

stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']

class BM25:
    def __init__(self, model, aver_idf):
        self.model = model
        self.idf = aver_idf

def tokenization(line : str):
    result = []
    words = pseg.cut(line)
    for word, flag in words:
        if word not in stopwords:
            result.append(word)
    return result

def generate_corpus(lines : list):
    corpus = []
    for line in lines:
        corpus.append(tokenization(line))
    return corpus

def get_BM25(corpus):
    bm25Model = BM25Okapi(corpus)
    return bm25Model

def search(model : BM25, query):
    words = tokenization(query)
    scores = model.get_scores(words)
    return np.argsort(scores)[::-1]
