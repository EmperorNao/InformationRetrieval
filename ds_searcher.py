import argparse
import json
import os

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from text_utils import preprocess_text


def jaccard_similarity(s1, s2):
    sim = len(s1.intersection(s2)) / len(s1.union(s2))
    return sim


def load_words(input_path):
    with open(os.path.join(input_path, "index.json")) as fname:
        index = json.load(fname)

    words_by_corpus = []
    for fname in index.keys():
        file_path = os.path.join(input_path, fname)
        with open(file_path) as doc_file:
            text = doc_file.read()
            words_by_corpus.append(text.split("\n"))
    return words_by_corpus


def ds_searcher(args):
    input_path = args.db_path
    processed_query = preprocess_text(args.query)
    query_set = set(processed_query.split())

    words_by_corpus = list(map(lambda x: set(x), load_words(input_path)))
    sims = []
    for word in words_by_corpus:
        sims.append(jaccard_similarity(query_set, word))
    top_sims = np.argsort(sims)[::-1][:args.top_k]

    with open(os.path.join(input_path, "index.json")) as fname:
        index = json.load(fname)

    output_names = []
    for index_sim in top_sims:
        output_names.append([sims[index_sim], index[f"{index_sim}.txt"]])

    return output_names


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, required=True)
    parser.add_argument('--db-path', type=str, required=True)
    parser.add_argument('--top-k', type=int, required=False, default=10)
    args = parser.parse_args()
    output = list(filter(lambda x: x[0] != 0.0, ds_searcher(args)))
    print(f"Top {args.top_k} docs for query {args.query}:")
    for sim, name in output:
        print(f"Doc name '{name}' with sim {sim}")
