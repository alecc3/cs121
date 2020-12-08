# import json
# from bs4 import BeautifulSoup
# from collections import defaultdict
# from nltk.tokenize import RegexpTokenizer
# from nltk.stem.snowball import EnglishStemmer
# from stop_words import get_stop_words
# import io
# import lxml
# import pickle
# import math
# import re
# import os
# from os import path
# from pathlib import Path

# from Indexer import *

# # Andrew Wang Chen, 31345312
# # Alec Chen, 47004754
# # Harkirat Sidhu, 11126100
# # Sadhika Yamasani, 70034981

# result = []
# def osPath(url):
#     files = os.listdir(url)  # 此时files是一个容器
#     for f in files:  # 遍历容器
#         real_path = path.join(url, f)  # 拼接路径
#         if path.isfile(real_path):  # 判断是否是文件
#             result.append(path.abspath(real_path))
#         elif path.isdir(real_path):  # 判断是否是文件夹
#             # 此时是一个文件夹
#             # 需要使用递归继续进行查找
#             osPath(real_path)  # 继续调用函数完成递归
#         else:
#             print("其他情况")
#             pass
# url1 = "C:\\Users\\andrew\\Downloads\\developer\\DEV" # Change this on your own system
# osPath(url1)
# folder_list = result

# index = Indexer(folder_list)
# index.buildInvertedIndex()
# print("Index done")

# index.get_query()

# # def open_test_data(i):
# #     return open(f'data{i}.pickle', 'rb')
# # for i in range(5):
# #     with open_test_data(i) as f:
# #         print("File", i)
# #         d = pickle.load(f)
# #         print(d.keys())


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

from Indexer import Indexer


result = []


def osPath(url):
    files = os.listdir(url)
    for f in files:
        real_path = path.join(url, f)
        if path.isfile(real_path):
            result.append(path.abspath(real_path))
        elif path.isdir(real_path):
            osPath(real_path)
        else:
            pass


url1 = "./DEV" # Change this on your own system
osPath(url1)

folder_list = result

index = Indexer(folder_list)
index.buildInvertedIndex()
index.merge_index()
index.get_query()