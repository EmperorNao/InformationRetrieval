import argparse
import json
import os
import shutil

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from text_utils import process_corpus


def get_corpus_with_index(input_path):
    corpus = []

    index_path = os.path.join(input_path, "index.json")
    with open(index_path) as json_file:
        index = json.load(json_file)

    for fname, docname in index.items():
        fname_path = os.path.join(input_path, fname)
        with open(fname_path) as doc_file:
            text = doc_file.read()
            corpus.append(text)

    return corpus, index


def save_words(output_path, words_by_corpus):
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    for i, words in enumerate(words_by_corpus):
        file_path = os.path.join(output_path, f"{i}.txt")
        with open(file_path, "w") as ofile:
            ofile.write("\n".join(words))


def db_transform(args):
    input_path = args.parsed_path
    output_path = args.db_path
    top_k = args.top_k

    corpus, index = get_corpus_with_index(input_path)
    processed_corpus = process_corpus(corpus)

    vectorizer = TfidfVectorizer()
    texts_idf = vectorizer.fit_transform(processed_corpus).todense()
    words = vectorizer.get_feature_names_out()
    words_indexes = np.argsort(texts_idf, axis=1)[:, ::-1]
    top_words = words[words_indexes][:, :top_k]

    save_words(output_path, top_words)
    shutil.copyfile(os.path.join(input_path, "index.json"), os.path.join(output_path, "index.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--parsed-path', type=str, required=True)
    parser.add_argument('--db-path', type=str, required=True)
    parser.add_argument('--top-k', type=int, required=False, default=50)
    args = parser.parse_args()
    db_transform(args)

