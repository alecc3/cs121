import json
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import EnglishStemmer
import io
import lxml
import pickle
import math
import re
import os
from os import path

# Alec Chen 47004754
# Harkirat Sidhu, 11126100

class Indexer:
    def __init__(self, paths):
        self.folder_list = paths
        self.index = {}
        self.count = 0

    def tokenize(self, folder_path):
        # tf score = count / total words
        # idf score = log total documents// documents that contain the token
        # tokenizer = RegexpTokenizer(r'\w+')
        stemmer = EnglishStemmer()
        wordsDict = {}
        i = 0
        # word_position = 0

        body = ''
        title = ''
        h1 = ''
        h2 = ''
        h3 = ''
        bold = ''
        strong = ''
        data = open(folder_path).read()
        for i in BeautifulSoup(data, "lxml").find_all("html"):
            body = i.text + body + ' '
        body_t = RegexpTokenizer(r'\w+').tokenize(body)

        for i in BeautifulSoup(data, "lxml").find_all("p"):
            title = i.text + title + ' '
            break
        title_t = RegexpTokenizer(r'\w+').tokenize(title)
        # title_t = title_t.lower()

        for i in BeautifulSoup(data, "lxml").find_all("h1"):
            h1 = i.text + h1 + " "
        h1_t = RegexpTokenizer(r'\w+').tokenize(h1)
        # h1_t = h1_t.lower()

        for i in BeautifulSoup(data, "lxml").find_all("h2"):
            h2 = i.text + h2 + " "
        h2_t = RegexpTokenizer(r'\w+').tokenize(h2)
        # h2_t = h2_t.lower()

        for i in BeautifulSoup(data, "lxml").find_all("h3"):
            h3 = i.text + h1 + " "
        h3_t = RegexpTokenizer(r'\w+').tokenize(h3)
        # h3_t = h3_t.lower()

        for i in BeautifulSoup(data, "lxml").find_all("b"):
            bold = i.text + bold + " "
        bold_t = RegexpTokenizer(r'\w+').tokenize(bold)
        # bold_t = bold_t.lower()

        for i in BeautifulSoup(data, "lxml").find_all("strong"):
            strong = i.text + strong + " "
        strong_t = RegexpTokenizer(r'\w+').tokenize(strong)
        # strong_t = strong_t.lower()

        # print("Folder: ", folder_path)

        for word in body_t:
            word = stemmer.stem(word)
            if word.lower() in wordsDict.keys():
                wordsDict[word.lower()][0] += 1
                # wordsDict[word.lower()].append(word_position)
                # word_position += 1
            else:
                wordsDict[word.lower()] = []
                wordsDict[word.lower()].append(1)
                # wordsDict[word.lower()].append(word_position)
                # word_position += 1

        counter = 0
        if len(title_t) > 0:
            for word in title_t:
                wordsDict[word.lower()][0] += 9
                counter += 1
                if counter == 10:
                    break

        if len(h1_t) > 0:
            for word in h1_t:
                if word.lower in wordsDict.keys():
                    wordsDict[word.lower()][0] += 6
        if len(h2_t) > 0:
            for word in h2_t:
                if word.lower in wordsDict.keys():
                    wordsDict[word.lower()][0] += 6
        if len(h3_t) > 0:
            for word in h3_t:
                if word.lower in wordsDict.keys():
                    wordsDict[word.lower()][0] += 6
        if len(bold_t) > 0:
            for word in bold_t:
                if word.lower in wordsDict.keys():
                    wordsDict[word.lower()][0] += 4
        if len(strong_t) > 0:
            for word in strong_t:
                if word.lower in wordsDict.keys():
                    wordsDict[word.lower()][0] += 4

        # print(wordsDict)

        for k,v in wordsDict.items():
            # posting = [tf-score, path]
            wordsDict[k] = [v[0]/len(wordsDict), folder_path]

        return wordsDict


    def buildInvertedIndex(self):
        # pages = [file_paths]
        # key = token:[Tuple(doc id, tf-idf score)]
        pages = self.folder_list
        for file in pages:
            self.count += 1
            tokens = self.tokenize(file)
            for token, posting in tokens.items():
                if token not in self.index:
                    index[token] = [posting]
                else:
                    index[token].append(posting)
        return

    def calculateIDF(self):
        for token, postings in self.index.items():
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
            pickle.dump(target, handle)


    def getNumber(self):
        return self.Count


result = []
def osPath(url):
    files = os.listdir(url)  # 此时files是一个容器
    for f in files:  # 遍历容器
        real_path = path.join(url, f)  # 拼接路径
        if path.isfile(real_path):  # 判断是否是文件
            result.append(path.abspath(real_path))
        elif path.isdir(real_path):  # 判断是否是文件夹
            # 此时是一个文件夹
            # 需要使用递归继续进行查找
            osPath(real_path)  # 继续调用函数完成递归
        else:
            print("其他情况")
            pass
url1 = r"./DEV"
osPath(url1)
folder_list = result

try:
    index = Indexer(folder_list)
    index.buildInvertedIndex()
    index.calculateIDF()
    index.write_to_file()
except:
    print("Failed")

# key = token:[Tuple(doc id, tf-idf score)]

"""
    for a in folder_list1:
        temp = Indexer(a, folder_list1)
        invertedIndex = temp.buildInvertedIndex()
        temp.write_to_file(invertedIndex)
        number_of_file = temp.getNumber()
"""