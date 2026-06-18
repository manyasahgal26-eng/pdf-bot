import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer


TERMS_FILE = Path("data/document_terms.json")
TERMS_FILE.parent.mkdir(exist_ok=True)


def extract_document_terms(chunks: list[dict], max_terms: int = 300) -> list[str]:
    texts = [chunk["text"] for chunk in chunks if chunk.get("text")]

    if not texts:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 3),
        max_features=max_terms,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b",
    )

    matrix = vectorizer.fit_transform(texts)
    terms = vectorizer.get_feature_names_out()
    scores = matrix.sum(axis=0).A1

    ranked_terms = sorted(
        zip(terms, scores),
        key=lambda item: item[1],
        reverse=True,
    )

    return [term for term, score in ranked_terms]


def save_document_terms(filename: str, terms: list[str]) -> None:
    existing_data = {}

    if TERMS_FILE.exists():
        with TERMS_FILE.open("r", encoding="utf-8") as file:
            existing_data = json.load(file)

    existing_data[filename] = terms

    with TERMS_FILE.open("w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=2)


def load_all_terms() -> list[str]:
    if not TERMS_FILE.exists():
        return []

    with TERMS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    terms = []

    for document_terms in data.values():
        terms.extend(document_terms)

    return sorted(set(terms))