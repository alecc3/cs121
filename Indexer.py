import json
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import EnglishStemmer
from stop_words import get_stop_words
import io
import lxml
import pickle
import math
import re
import os
from os import path
from pathlib import Path


class Indexer:
    def __init__(self, paths):
        self.folder_list = paths
        self.index = {}
        self.count = 0
        self.stop_words = get_stop_words('english')


    def tokenize(self, file):
        stemmer = EnglishStemmer()
        url = open(file, encoding='utf-8')

        html = url.read()
        soup = BeautifulSoup(html, 'lxml')

        for script in soup(['script', 'style']):
            script.decompose()
            
        word_weights = dict()
        for i in BeautifulSoup(html, "lxml").find_all(['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'strong', 'p']):
            tokens = re.findall(r'\w+', i.text)
            weight = None

            if i.name == 'title':
                weight = 20
            elif i.name == 'strong' or i.name == 'b' or i.name[0] == 'h':
                weight = 10
            else:
                weight = 4
            
            for word in tokens:
                word_stem = stemmer.stem(word).lower()
                if word_stem not in word_weights:
                    word_weights[word_stem] = weight
                else:
                    word_weights[word_stem] += weight

        url.close()
        return word_weights


    def buildInvertedIndex(self):
        # pages = [file_paths]
        # key = token:[Tuple(doc id, tf-idf score)]
        pages = self.folder_list
        for file in pages:
            self.count += 1
            tokens = self.tokenize(file)
            print("File:",file)
            for token, tf in tokens.items():
                if token not in self.index:
                    self.index[token] = [[tf, file]]
                else:
                    self.index[token].append([tf, file])

    def printIndex(self):
        for k,v in self.index.items():
            print(k,len(v))

    def calculateIDF(self):
        for _, postings in self.index.items():
            df = len(postings)
            idf = math.log10(self.count / (df))
            for i in range(len(postings)): # each individual posting
                tf = postings[i][0]
                tf_idf = tf * idf
                postings[i][0] = tf_idf


    def write_to_file(self):
        with open('index.pickle', 'wb') as handle:
            # index with #s pertaining to your index
            # # of documents (self.count)
            # # of tokens (len(self.index))
            # total size of index (in KB)
            pickle.dump(self.index, handle)
        kilobytes = Path('index.pickle').stat().st_size//1024
        f = open("report.txt","w")
        f.write("# documents: " + str(self.count) + "\n")
        f.write("# tokens: " + str(len(self.index)) + "\n")
        f.write("Total size: " + str(kilobytes) + "kb")

