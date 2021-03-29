import math
import json
import psycopg2
import psycopg2.extras
from nltk.stem import PorterStemmer
from ANALYST.indexer import tokenize
import operator
import numpy as np
import time

def get_input():
    # Get the users input query and return it

    query = input()
    return query


def porter_query(query):
    # Takes inputted query and converts each word into a porter stem

    words = tokenize(query.lower())
    ps = PorterStemmer()
    stemmed = [ps.stem(i.strip()) for i in words]

    return stemmed


def filter_words(words, indexes):

    final = []
    for i in words:
        if i in indexes.keys():
            final.append(i)

    return final


def get_query_indexes(stemmed, indexes):
    # Take the stemmed words and return a dictionary containing all of the word values
    # inside of the indexer

    relevant = {}

    for i in stemmed:
        try:
            relevant[i] = indexes[i]
        except KeyError:
            pass

    return relevant

def database_to_dict(words):
    # Take indexes stored in database and turn it back into a dict

    indexes = {}
    word_count = 0
    state = "SELECT * FROM indexer WHERE "

    for i in words:
        if word_count == 0:
            state = state + "keys = '{}'".format(i)
            word_count = word_count + 1
        else:
            state = state + " OR " + "keys = '{}'".format(i)
    state = state + ";"
    conn = psycopg2.connect(host="localhost", database="postgres", port=5432, user="postgres", password="Aki12345+")

    # import in all of the keys
    cur = conn.cursor()
    cur.execute(state)
    keys = cur.fetchall()

    # close connection
    cur.close()
    conn.close()

    # create indexer
    index_count = 0
    for key in keys:

        indexes[key[0]] = json.loads(key[1].replace("'", '"'))
        index_count = index_count + 1

    return indexes


def calc_tfi(param1, param2):
    # Calculates the tfi score for the given doc and word index

    score = param1 * (math.log(1988 / (param2 + 1)))

    return score


def tfi_scores(words, ex_indexes):
    # Will calculate the tfi score for each of the documents found in each of the
    # relevant indexes.

    scores = {}
    count = 0

    for i in words:
        param2 = len(ex_indexes[i])
        for doc in ex_indexes[i].keys():
            param1 = ex_indexes[i][doc]
            score = calc_tfi(param1, param2)

            if doc in scores:
                scores[doc][count] = score
            else:
                scores[doc] = [0] * len(words)
                scores[doc][count] = score

        count = count + 1

    return scores


def get_query_counts(words):
    # Gets the count that each unique word appears in the query

    placers = list(set(words))
    counts = [0] * len(placers)

    for word in words:
        counts[placers.index(word)] = counts[placers.index(word)] + 1

    return counts


def cosine_similarity(x, y):
    # Calculates the cosine similarity between the docs scores and the word counts

    num = x.dot(y.T)
    nom = np.linalg.norm(x) * np.linalg.norm(y)

    return num / nom


def cosine_scores(scores, word_counts):
    # Calculates the cosine similarity for each of the docs in the dictionary

    cosines = {}
    for i in scores.keys():
        cosines[i] = (cosine_similarity(np.array(scores[i]).reshape(len(scores[i]), 1), np.array(word_counts).reshape(len(word_counts), 1)))

    return cosines


def flatten_scores(scores):
    # takes all of the list embedded scores and will convert it into a single list

    for i in scores.keys():
        scores[i] = [item for elem in scores[i] for item in elem]

    return scores

def mean_scores(scores):
    # Takes all of the scores calculated in the cosine similarity and
    # stores the mean of all those scores

    for i in scores.keys():
        scores[i] = np.mean(scores[i])

    return scores


def get_url(path):
    # Retrieves the url from the json file

    with open(path, "r") as read_file:
        f = json.load(read_file)
    return f["url"]

if __name__ == '__main__':

    running = True
    while running:
        # Retrieve the users input
        print("Enter Query: ")
        query = get_input()

        # Convert the words using Porter Stemming
        words = porter_query(query)

        # Get all of the indexes from the database and turn it back into a dict
        indexes = database_to_dict(words)

        # End program if keys not found in index
        if indexes == {}:
            print("No Results Found")
            exit()

        # Check what words were found in the indexer
        words = filter_words(words, indexes)

        # Start the time the query is running
        startTime = time.time()

        # Get a list of how many times each word appears in the query
        word_counts = get_query_counts(words)

        # Create a set of unique words in the query
        words = set(words)

        # extract only the indexes that are needed by the words in the query
        ex_indexes = get_query_indexes(words, indexes)

        # Retrieve the tf-idf scores for each of the words for each of the docs
        scores = tfi_scores(words, ex_indexes)

        # Calculate the cosine similarity scores for each of the docs
        cos_scores = cosine_scores(scores, word_counts)

        # Turn the embedded list into a single list
        cos_scores = flatten_scores(cos_scores)

        # Aggregate all of the cosine scores into one single score
        cos_scores = mean_scores(cos_scores)

        # Sort all of the items of the dictionary so that the docs with the highest cosine similarity
        # scores appear in the front
        cos_scores = sorted(cos_scores.items(), key=operator.itemgetter(1), reverse=True)

        count = 0
        # Print the top 5 relevant pages
        for i in cos_scores:
            print(get_url(i[0]))
            count = count + 1
            if count == 5:
                break
            else:
                continue

        # Print out how long it took to execute the search results (seconds)
        executionTime = (time.time() - startTime)
        print('Execution time in seconds: ' + str(executionTime))








