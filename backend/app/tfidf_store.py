import json
import math
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# In-memory store: maps filename -> list of chunks
stored_chunks: dict[str, list[dict]] = {}

CHUNKS_DIR = Path("data/chunks")
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)


def add_chunks(chunks: list[dict], filename: str) -> int:
    if not chunks:
        return 0

    file_chunks = []
    for chunk in chunks:
        file_chunks.append({
            "text": chunk["text"],
            "metadata": {
                "filename": filename,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
            },
        })

    # Save in-memory
    stored_chunks[filename] = file_chunks

    # Save to disk to survive server restarts/sleeps
    chunk_file = CHUNKS_DIR / f"{filename}.json"
    try:
        with chunk_file.open("w", encoding="utf-8") as f:
            json.dump(file_chunks, f, indent=2)
    except Exception as e:
        print(f"Error saving chunks to disk: {e}")

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


def search_chunks(question: str, filename: str = None, top_k: int = 5) -> list[dict]:
    if not filename:
        return []

    # Try loading from disk if not in memory (e.g. after server sleep/restart)
    if filename not in stored_chunks:
        chunk_file = CHUNKS_DIR / f"{filename}.json"
        if chunk_file.exists():
            try:
                with chunk_file.open("r", encoding="utf-8") as f:
                    stored_chunks[filename] = json.load(f)
            except Exception as e:
                print(f"Error loading chunks from disk: {e}")
                return []
        else:
            return []

    chunks_to_search = stored_chunks[filename]
    if not chunks_to_search:
        return []

    expanded_question = expand_query(question)
    documents = [chunk["text"] for chunk in chunks_to_search]

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

        chunk = chunks_to_search[int(index)]

        matches.append({
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "distance": 1 - similarity,
        })

    return matches

