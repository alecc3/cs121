# Alec Chen, 47004754
# Andrew Wang Chen, 31345312
# Harkirat Sidhu, 11126100
# Sadhika Yamasani, 70034981

import json
import pickle

import io
import os
from os import path
from pathlib import Path

import lxml
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import EnglishStemmer
from stop_words import get_stop_words

import math
import re
import time


# Five bookkeeping indices for the five text files
# store the line numbers of tokens.
bookkeeper0 = dict()
bookkeeper1 = dict()
bookkeeper2 = dict()
bookkeeper3 = dict()
bookkeeper4 = dict()


len_posting_bookkeeper = defaultdict(int)

class Posting:
    def __init__(self, f, t):
        # File ID is an integer
        self.file_id = f
        self.tf = math.log10(1+t)
        self.tfidf = 0.
        # self.positions = []
        # self.field = {}


    def get_tf(self):
        return self.tf
    

    def __str__(self):
        return str(self.file_id) + ' ' + str(self.tfidf)



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
        self.merged_bookkeeper = dict()


    # Returns {str:int} representing {token:token_frequency}
    # token_frequency may be more accurately described as weights.
    def tokenize(self, file):
        stemmer = EnglishStemmer()
        # start_time = time.time()
        url = open(file, encoding='utf-8')
        html = url.read()
        soup = BeautifulSoup(html, 'lxml')
        for script in soup(['script', 'style']):
            script.extract()
        word_weights = defaultdict(int)
        # total_words = len(soup.get_text())
        # Index position: index in tokens, creation of auxiliary
        for i in soup.find_all(['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'strong', 'p']):
            tokens = set()
            for t in re.findall(r'\w+', i.text):
                if len(t) >= 2:
                    tokens.add(t.lower())
            weight = [1,4,10]
            for token in tokens:
                token = stemmer.stem(token)
                if i.name == 'title':
                    word_weights[token] += weight[2]
                elif i.name == 'strong' or i.name == 'b' or i.name[0] == 'h':
                    word_weights[token] += weight[1]
                else:
                    word_weights[token] += weight[0]
        url.close()
        # print(time.time() - start_time, "seconds")
        return word_weights


    def file_to_int(self,file):
        if file in self.file_mapping:
            return self.file_mapping[file]
        # Maps current integer to file
        self.file_mapping[file] = self.url_map_count
        self.url_map_count += 1
        return self.file_mapping[file]

    
    def buildInvertedIndex(self):
        # pages: array of file paths
        # Key: token of format str
        # Value: list of tuples of format (document ID, tf-idf score)
        pages = self.folder_list
        # c = 0
        batch = []
        step = 10
        i = 0
        while i+step < 51:
            # Get a fixed-size batch
            batch = pages[i:i+step]
            for file in batch:
                tokens = self.tokenize(file) # Parses into tokens, which are stems
                file_id = self.file_to_int(file)
                for id,tf in tokens.items():
                    if id not in self.index:
                        self.index[id] = []
                    self.index[id].append(Posting(file_id, tf))
                self.count += 1
            self.calculateIDF()
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
            for p in postings: # For each individual posting...
                tf = p.get_tf()
                tf_idf = tf * idf
                p.tfidf = tf_idf

    ##############################################################################################  
    # TODO: FINISH, TEST, TROUBLESHOOT, AND REVISE THIS SECTION ##################################
    ##############################################################################################
    def merge_index(self):
        merged_index = open('index.txt', 'w+')

        with open('data0.txt', 'r+') as f0, open('data1.txt', 'r+') as f1, \
            open('data2.txt', 'r+') as f2, open('data3.txt', 'r+') as f3, \
            open('data4.txt', 'r+') as f4:
            
            # Set that tracks tokens that have been seen before
            seen = set()
            line_num = 1

            lines = f0.readlines()
            for line in lines:
                merged_index.write(line[:-1])
                tokens = line.split()
                term = tokens[0]
                seen.add(term)

                self.merged_bookkeeper[term] = line_num
                line_num += 1

                if term in bookkeeper1:
                    for _ in range(bookkeeper1[term] - 1):
                        __ = f1.readline()
                    temp_line = f1.readline()
                    temp_tokens = temp_line.split()

                    for i in range(1, len(temp_tokens), 2):
                        merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                if term in bookkeeper2:
                    for _ in range(bookkeeper2[term] - 1):
                        __ = f2.readline()
                    temp_line = f2.readline()
                    temp_tokens = temp_line.split()

                    for i in range(1, len(temp_tokens), 2):
                        merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                if term in bookkeeper3:
                    for _ in range(bookkeeper3[term] - 1):
                        __ = f3.readline()
                    temp_line = f3.readline()
                    temp_tokens = temp_line.split()

                    for i in range(1, len(temp_tokens), 2):
                        merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                if term in bookkeeper4:
                    for _ in range(bookkeeper4[term] - 1):
                        __ = f4.readline()
                    temp_line = f4.readline()
                    temp_tokens = temp_line.split()

                    for i in range(1, len(temp_tokens), 2):
                        merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                merged_index.write('\n')

            
            lines = f1.readlines()
            for line in lines:
                tokens = line.split()
                term = tokens[0]
                if term not in seen:
                    seen.add(term)
                    merged_index.write(line)

                    self.merged_bookkeeper[term] = line_num
                    line_num += 1

                    if term in bookkeeper2:
                        for _ in range(bookkeeper2[term] - 1):
                            __ = f2.readline()
                        temp_line = f2.readline()
                        temp_tokens = temp_line.split()

                        for i in range(1, len(temp_tokens), 2):
                            merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                    if term in bookkeeper3:
                        for _ in range(bookkeeper3[term] - 1):
                            __ = f3.readline()
                        temp_line = f3.readline()
                        temp_tokens = temp_line.split()

                        for i in range(1, len(temp_tokens), 2):
                            merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                    if term in bookkeeper4:
                        for _ in range(bookkeeper4[term] - 1):
                            __ = f4.readline()
                        temp_line = f4.readline()
                        temp_tokens = temp_line.split()

                        for i in range(1, len(temp_tokens), 2):
                            merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                    merged_index.write('\n')

                
            lines = f2.readlines()
            for line in lines:
                tokens = line.split()
                term = tokens[0]
                if term not in seen:
                    seen.add(term)
                    merged_index.write(line)

                    self.merged_bookkeeper[term] = line_num
                    line_num += 1

                    if term in bookkeeper3:
                        for _ in range(bookkeeper3[term] - 1):
                            __ = f3.readline()
                        temp_line = f3.readline()
                        temp_tokens = temp_line.split()

                        for i in range(1, len(temp_tokens), 2):
                            merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                    if term in bookkeeper4:
                        for _ in range(bookkeeper4[term] - 1):
                            __ = f4.readline()
                        temp_line = f4.readline()
                        temp_tokens = temp_line.split()

                        for i in range(1, len(temp_tokens), 2):
                            merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                    merged_index.write('\n')


            lines = f3.readlines()
            for line in lines:
                tokens = line.split()
                term = tokens[0]
                if term not in seen:
                    seen.add(term)
                    merged_index.write(line)

                    self.merged_bookkeeper[term] = line_num
                    line_num += 1

                    if term in bookkeeper4:
                        for _ in range(bookkeeper4[term] - 1):
                            __ = f4.readline()
                        temp_line = f4.readline()
                        temp_tokens = temp_line.split()

                        for i in range(1, len(temp_tokens), 2):
                            merged_index.write(' ' + temp_tokens[i] + ' ' + temp_tokens[i+1])

                    merged_index.write('\n')


            lines = f4.readlines()
            for line in lines:
                tokens = line.split()
                term = tokens[0]
                if term not in seen:
                    seen.add(term)
                    merged_index.write(line)

                    self.merged_bookkeeper[term] = line_num
                    line_num += 1

                    merged_index.write('\n')


        merged_index.close()
            # for i in range(1,5):
            #     exec('lines = f' + i + '.readlines()')
            #     for line in lines:
            #         tokens = line.split()
            #         term = tokens[0]
            #         if term in seen:
            #             temp_line_num = bookkeeper[term]
            #             merged_index.seek(0, os.SEEK_SET)
            #             for _ in range(temp_line_num):
            #                 merged_index.readline()
            #             merged_index.seek(-1, os.SEEK_CUR)
            #             old = merged_index.read()
            #             for k in range(1, len(tokens), 2):
            #                 pass


            # # In each round of the loop, read one line from each of the five files.
            # for i in range(5):
            #     tokens = []
            #     # Each line has the following format:
            #     #   'term posting1_fileID posting1_tfidf posting2_fileID posting2_tfidf ' + ...
            #     #   + ' postingN_fileID postingN_tfidf\n' 
            #     exec('tokens = f' + i + '.readline().split()')
                
            #     if tokens[i] not in seen:
            #         seen.add(tokens[0])
            #         merged_index.write(tokens[0] + ' ')



    def get_query(self):
        def get_postings(line):
            res = ""
            with open('index.txt', 'r+') as handle:
                for _ in range(line - 1):
                    handle.readline()
                res = handle.readline()
            return res

        stemmer = EnglishStemmer()
        postings = []
        query = input('Enter search query: ')
        tokens = query.split(' ')
        k = self.merged_bookkeeper
        for token in tokens:
            stem = stemmer.stem(token)
            postings.append(get_postings(k[stem]))
        matches=self.intersect(postings)
        print(self.top_5(matches))
        return


    def merge(self, posting1, posting2):
        d = defaultdict(int)
        for i in range(len(posting1)):
            d[posting1[i]] += 1
        for i in range(len(posting2)):
            d[posting2[i]] += 1
        return [p for p in d.keys() if d[p] >= 2] # intersections

    def convert_list_tuple(self,s):
        s = s.split()[1:] # parse out token
        res = []
        for i in range(1, len(s),2):
            p = (s[i - 1], s[i]) # create tuple
            res.append(p)
        return res


    def intersect(self, postings):
        postings.sort(key=len)
        postings = [self.convert_list_tuple(p) for p in postings]
        merged=self.merge(postings[0],postings[1])
        i=2
        while i<len(postings)-1:
            merged=self.merge(merged,postings[i])
            i+=1
        return merged


    def top_5(self, merged):
        merged = sorted(merged,key=lambda x:x[1],reverse=True)
        res = []
        for tup in merged:
            for k,v in self.file_mapping.items():
                if len(res) == 5: break
                if v == int(tup[0]):
                    res.append(k)
        return res

    def write_to_file(self):
        with open(f'data{self.f_count}.txt', 'w+') as handle:
            line_num = 1
            for tok, postings in self.index.items():
                handle.write(tok)
                for posting in postings:
                    handle.write(' ' + str(posting))
                    len_posting_bookkeeper[tok] += 1
                handle.write('\n')
                # Each line has the following format:
                #   'term posting1_fileID posting1_tfidf posting2_fileID posting2_tfidf ' + ...
                #   + ' postingN_fileID postingN_tfidf\n' 

                exec('bookkeeper' + str(self.f_count) +'[tok] = line_num')
                # For example, if self.f_count==0, then exec() will
                # run the assignment statement
                #   bookkeeper0[tok] = line_num
                # as if it were an actual line of code.

                line_num += 1
        
        self.f_count += 1

