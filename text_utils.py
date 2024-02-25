from tqdm import tqdm
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    Doc
)

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stopwords_ru = stopwords.words('russian')


def lemmatize_text(text: str) -> Doc:
    if not lemmatize_text.initialized:
        lemmatize_text.initialized = True
        lemmatize_text.segmenter = Segmenter()
        lemmatize_text.morph_vocab = MorphVocab()
        lemmatize_text.emb = NewsEmbedding()

        lemmatize_text.emb = NewsEmbedding()
        lemmatize_text.morph_tagger = NewsMorphTagger(lemmatize_text.emb)
        lemmatize_text.syntax_parser = NewsSyntaxParser(lemmatize_text.emb)

    doc = Doc(text)
    doc.segment(lemmatize_text.segmenter)
    doc.tag_morph(lemmatize_text.morph_tagger)
    for token in doc.tokens:
        token.lemmatize(lemmatize_text.morph_vocab)
    return doc


lemmatize_text.initialized = False


def get_lemmatized_tokens(doc: Doc) -> list[str]:
    return [token.lemma for token in doc.tokens]


def remove_stop_words(tokens: list[str]) -> list[str]:
    return list(filter(lambda x: x not in stopwords_ru, tokens))


def join_tokens(tokens: list[str]) -> str:
    return " ".join(tokens)


def preprocess_text(text: str) -> str:
    doc = lemmatize_text(text)
    return join_tokens(remove_stop_words(get_lemmatized_tokens(doc)))


def process_corpus(corpus: list[str]) -> list[str]:
    out = []
    for text in tqdm(corpus):
        out.append(preprocess_text(text))
    return out
