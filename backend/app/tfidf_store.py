import math

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


stored_chunks: list[dict] = []


def add_chunks(chunks: list[dict], filename: str) -> int:
    if not chunks:
        return 0

    stored_chunks.clear()

    for chunk in chunks:
        stored_chunks.append({
            "text": chunk["text"],
            "metadata": {
                "filename": filename,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
            },
        })

    return len(chunks)


def expand_query(question: str) -> str:
    question_lower = question.lower()

    if any(word in question_lower for word in ["what is", "what are", "define", "meaning"]):
        return f"{question} definition meaning explanation overview"

    if any(word in question_lower for word in ["how", "explain"]):
        return f"{question} steps process explanation details"

    if "why" in question_lower:
        return f"{question} reason cause purpose explanation"

    return question


def search_chunks(question: str, top_k: int = 5) -> list[dict]:
    if not stored_chunks:
        return []

    expanded_question = expand_query(question)
    documents = [chunk["text"] for chunk in stored_chunks]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000,
    )

    matrix = vectorizer.fit_transform(documents + [expanded_question])
    document_matrix = matrix[:-1]
    query_vector = matrix[-1]

    similarities = cosine_similarity(query_vector, document_matrix)[0]
    ranked_indexes = similarities.argsort()[::-1][:top_k]

    matches = []

    for index in ranked_indexes:
        similarity = float(similarities[index])

        if math.isclose(similarity, 0.0):
            continue

        chunk = stored_chunks[int(index)]

        matches.append({
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "distance": 1 - similarity,
        })

    return matches
