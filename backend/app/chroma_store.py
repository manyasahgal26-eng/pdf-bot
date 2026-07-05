import chromadb

from app.embeddings import create_embedding, create_embeddings


client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_or_create_collection(name="documents")


def add_chunks(chunks: list[dict], filename: str) -> int:
    if not chunks:
        return 0

    texts = [chunk["text"] for chunk in chunks]
    ids = [f"{filename}-{chunk['id']}" for chunk in chunks]

    metadatas = [
        {
            "filename": filename,
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
        }
        for chunk in chunks
    ]

    embeddings = create_embeddings(texts)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

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
    expanded_question = expand_query(question)
    question_embedding = create_embedding(expanded_question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
    )

    matches = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        matches.append({
            "text": document,
            "metadata": metadata,
            "distance": distance,
        })

    return matches
