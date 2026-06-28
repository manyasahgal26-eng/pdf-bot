from app.vector_store import search_chunks
from app.llm import generate_answer
from app.web_search import get_web_context


MAX_RELEVANCE_DISTANCE = 22


def format_sources(matches: list[dict]) -> list[dict]:
    sources = []

    for match in matches:
        metadata = match["metadata"]

        sources.append({
            "filename": metadata.get("filename"),
            "page": metadata.get("page"),
            "chunk_index": metadata.get("chunk_index"),
            "distance": match.get("distance"),
        })

    return sources


def is_relevant(matches: list[dict]) -> bool:
    if not matches:
        return False

    best_distance = matches[0].get("distance")

    if best_distance is None:
        return False

    return best_distance <= MAX_RELEVANCE_DISTANCE


def build_source_text(sources: list[dict]) -> str:
    if not sources:
        return ""

    best_source = sources[0]
    filename = best_source.get("filename", "uploaded document")
    page = best_source.get("page", "unknown")

    return f"Source: {filename}, page {page}"


def answer_question(question: str, use_web: bool = False) -> dict:
    matches = search_chunks(question, top_k=5)
    document_sources = format_sources(matches)

    document_context_parts = []
    document_context = ""

    if is_relevant(matches):
        document_context_parts = [match["text"] for match in matches]
        document_context = "\n\n".join(document_context_parts)

    web_context = ""
    web_sources = []

    if use_web:
        web_result = get_web_context(question)
        web_context = web_result["context"]
        web_sources = web_result["sources"]

    if not document_context and not web_context:
        return {
            "answer": "I could not find this in the uploaded document or web sources.",
            "sources": [],
            "web_sources": [],
            "context": [],
        }

    combined_context = ""

    if document_context:
        combined_context += f"Uploaded document context:\n{document_context}\n\n"

    if web_context:
        combined_context += f"Web context:\n{web_context}\n\n"

    answer = generate_answer(question, combined_context)

    source_text = build_source_text(document_sources)

    if source_text:
        answer = f"{answer}\n\n{source_text}"

    return {
        "answer": answer,
        "sources": document_sources,
        "web_sources": web_sources,
        "context": document_context_parts,
    }