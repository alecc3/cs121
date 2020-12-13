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