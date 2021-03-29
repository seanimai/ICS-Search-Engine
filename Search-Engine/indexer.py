# Imported Libraries
import re
import os
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import json
import nltk
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import pandas as pd
import time
import psycopg2
import psycopg2.extras
from collections import defaultdict
from ANALYST.duplicate_remover import isNearDuplicate

bad = 0


def remove_duplicates():

    unique_count = 0
    unique_pages = []

    directory1 = "C:/Users/imaia/Desktop/CS121/HW#3/ANALYST/www_cs_uci_edu"
    directory2 = "C:/Users/imaia/Desktop/CS121/HW#3/ANALYST/www_informatics_uci_edu"
    directory3 = "C:/Users/imaia/Desktop/CS121/HW#3/ANALYST/www-db_ics_uci_edu"
    directories = [directory1, directory2, directory3]

    for dir in directories:
        for i in os.listdir(dir):

            full_path = '%s/%s' % (dir, i)
            f = open(full_path, 'r')
            data = json.loads(f.read())
            url = data['url']

            try:
                html = urlopen(url)
            except:
                pass

            soup = BeautifulSoup(html, 'html.parser')
            token_frequencies = computeTokenFrequencies(tokenize(soup.get_text(" ", True)))

            if isNearDuplicate(token_frequencies):
                pass
            else:
                unique_pages.append(full_path)
                unique_count = unique_count + 1

    print("There were {} unique pages found".format(unique_count))
    return unique_pages

def tokenize(content):
    regex = "[a-zA-Z0-9]+"
    pattern = re.compile(regex)

    tokens = pattern.findall(content)

    return tokens

def computeTokenFrequencies(tokens):
    d = defaultdict(int)
    for token in tokens:
        d[token] += 1
    return d


def remove_stop_words(tokens):
    stop_words = set(stopwords.words('english'))
    removed = [i for i in tokens if not i in stop_words]
    return removed


def porter_stemming(words):
    ps = PorterStemmer()
    stemmed = [ps.stem(i.strip()) for i in words]

    return stemmed


def get_bolded_words(data):
    bold_words = set()

    # Get the source url
    url = data['url']
    try:
        html = urlopen(url)
    except:
        global bad
        bad = bad + 1
        return set()
    # Get the html
    soup = BeautifulSoup(html, 'html.parser')

    # Retrieve all bold words from html
    for i in soup.find_all('b'):
        split = i.get_text().split(" ")
        for z in split:
            bold_words.add(z)

    if len(bold_words) == 0:
        return set()

    return porter_stemming(bold_words)


def get_headings(data):
    headings = set()

    # Get the source url
    url = data['url']

    try:
        html = urlopen(url)
    except:
        return set()

    # Get the html
    soup = BeautifulSoup(html, 'html.parser')

    h = ["h1", "h2", "h3"]
    # Retrieve all bold words from html
    for head in h:
        try:
            for i in soup.find_all(head):
                split = i.get_text().split(" ")
                for z in split:
                    headings.add(z)
        except:
            pass

    if len(headings) == 0:
        return set()

    return porter_stemming(headings)


def indexer():

    files = remove_duplicates()
    index = {}
    count = 0
    startTime = time.time()

    for i in files:
        try:
            f = open(i, 'r')
            data = json.loads(f.read())

            # Retrieve the content of the json file
            content = data['content']

            # Tokenize the content of the json file
            tokens = tokenize(content)

            # Remove stop words
            removed = remove_stop_words(tokens)

            # Porter Stem all of the words
            stemmed = porter_stemming(removed)

            # Get bolded words from json
            bolded = get_bolded_words(data)

            # Get all headings from json
            headings = get_headings(data)

            # Add the counts of words for the json file
            for stem in stemmed:
                if stem not in index:
                    index[stem] = {i: 1}
                elif i not in index[stem]:
                    index[stem][i] = 1
                else:
                    index[stem][i] = index[stem][i] + 1

            # Increase the frequency of each word if the word is bold
            for bold in bolded:
                if bold not in index:
                    pass
                elif i not in index[bold]:
                    index[bold][i] = 2
                else:
                    index[bold][i] = index[bold][i] + 2

            # Increase the frequency of each word if the word is a heading
            for head in headings:
                if head not in index:
                    pass
                elif i not in index[head]:
                    index[head][i] = 2
                else:
                    index[head][i] = index[head][i] + 2
        except:
            continue

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))

    # Store indexes in csv file
    conn = None
    try:
        conn = psycopg2.connect(host="localhost", database="postgres", port=5432, user="postgres", password="Aki12345+")

        command = "INSERT INTO indexer (keys, value) VALUES (%s, %s);"

        cur = conn.cursor()
        for key, value in index.items():
            cur.execute(command, (str(key), str(value)))

    except (Exception, psycopg2.DatabaseError):
        print("Could not connect to database")

    finally:
        if conn is not None:
            conn.commit()
            conn.close()
            cur.close()

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))
    print(count)

if __name__ == '__main__':

    indexer()
    dict_from_csv = pd.read_csv('indexes.csv', header=None, index_col=0, squeeze=True).to_dict()

    print("There are {} unique words".format(len(dict_from_csv.keys())))
