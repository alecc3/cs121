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
import time

class Posting:
    def __init__(self, t, f):
        self.tf = math.log10(1+t)
        self.tfidf = 0
        # file id as integer
        self.file_id = f
        self.positions = []
        self.field = {}
    def get_tf(self):
        return self.tf


class Indexer:
    def __init__(self, paths):
        self.folder_list = paths
        self.index = {}
        self.count = 0
        self.stop_words = get_stop_words('english')
        self.stemmer = EnglishStemmer()
        self.f_count = 0
        self.file_mapping = {}
        self.url_map_count = 0


    def tokenize(self, file):
        start_time = time.time()
        url = open(file, encoding='utf-8')
        html = url.read()
        soup = BeautifulSoup(html, 'lxml')
        for script in soup(['script', 'style']):
            script.extract()
        word_weights = defaultdict(int)
        #total_words = len(soup.get_text())

        # index position = index in tokens, create auxiliary
        for i in soup.find_all(['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'strong', 'p']):
            tokens = set()
            for t in re.findall(r'\w+', i.text):
                if len(t) >= 2:
                    tokens.add(t.lower())
            weight = [1,4,10]
            for token in tokens:
                if i.name == 'title':
                    word_weights[token] = weight[2]
                elif i.name == 'strong' or i.name == 'b' or i.name[0] == 'h':
                    word_weights[token] = weight[1]
                else:
                    word_weights[token] = weight[0]
        url.close()
        print(time.time() - start_time, "seconds")
        return word_weights

    def file_to_int(self,file):
        if file in self.file_mapping:
            return self.file_mapping[file]
        # map current integer to file
        self.file_mapping[file] = self.url_map_count
        self.url_map_count += 1
        return self.file_mapping[file]

    def buildInvertedIndex(self):
        # pages = [file_paths]
        # key = token:[Tuple(doc id, tf-idf score)]
        pages = self.folder_list
        c = 0
        batch = []
        step = 10
        i = 0
        while i+step < 51:
            # get batch
            batch = pages[i:i+step]
            for file in batch:
                print("File:", file)
                tokens = self.tokenize(file) # parse into tokens
                file_id = self.file_to_int(file)
                for id,tf in tokens.items():
                    if id in self.index:
                        self.index[id].append(Posting(tf, file_id))
                    else:
                        self.index[id] = []
                self.count += 1
            self.write_to_file()
            self.index = {}
            i += step


    def printIndex(self):
        for k,v in self.index.items():
            print(k,len(v))

    def calculateIDF(self):
        for _, postings in self.index.items():
            df = len(postings)
            idf = math.log10(self.count / 1+(df))
            for p in postings: # each individual posting
                tf = p.get_tf()
                tf_idf = tf * idf
                p.idf = tf_idf

    def get_query(self):
        stemmer = EnglishStemmer()
        postings = []
        query = input('Enter search query: ')
        tokens = query.split(' ')
        if len(tokens) < 2:
            stem = stemmer.stem(tokens[0])
            postings=self.index[stem]
            l = [(doc_id, tf) for doc_id, tf in postings.items()]
            l.sort(key=l[1], reverse=True)
            l = l[:5]
            print( [doc_id for doc_id, _ in l])
            #return self.top_5(self.index[stem])
        else:
            for token in tokens:
                stem = stemmer.stem(token)
                postings.append(self.index[stem])
            matches=intersect(postings)
            result=top_5(matches)
            print(result)



    def merge(self, posting1,posting2):
        res=[]
        i=0
        di=dict(posting2)
        while i<len(posting1):
            if posting1[i][0] in di.keys():
                res.append(posting1[i])
            i+=1
        return res



    def intersect(self, postings):
        postings.sort(key=len)
        merged=merge(postings[0],postings[1])
        i=2
        while i<len(postings)-1:
            merged=merge(merged,postings[i])
            i+=1
        return merged


    def top_5(self, merged):
        # posting = [(doc_id, tf-idf score)]
        #postings =[posting]
        #merged is a posting but with matching docs
        #l = [(doc_id, tf) for doc_id, tf in postings.items()]
        merged.sort(key=lambda tup: tup[1], reverse=True)
        result=[]
        count=0
        for doc_id, score in merged:
            if count==5:
                break
            elif doc_id not in result:
                result.append(doc_id)
            count += 1
        #merged.sort(key=merged[0][1], reverse=True)
        #merged= merged[:5]
        return result #[doc_id for doc_id, _ in merged]

    def write_to_file(self):
        with open(f'data{self.f_count}.pickle', 'wb') as handle:
            pickle.dump(self.index, handle)
        self.f_count += 1

    def generate_report(self):
        kilobytes = Path('index.pickle').stat().st_size//1024
        f = open("report.txt","w")
        f.write("# documents: " + str(self.count) + "\n")
        f.write("# tokens: " + str(len(self.index)) + "\n")
        f.write("Total size: " + str(kilobytes) + "kb")

