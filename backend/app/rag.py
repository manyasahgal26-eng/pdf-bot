from app.vector_store import search_chunks
from app.llm import generate_answer


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


def answer_question(question: str) -> dict:
    matches = search_chunks(question, top_k=5)

    if not is_relevant(matches):
        return {
            "answer": "I could not find this in the uploaded document.",
            "sources": [],
            "context": [],
        }

    context_parts = [match["text"] for match in matches]
    context = "\n\n".join(context_parts)

    answer = generate_answer(question, context)
    sources = format_sources(matches)
    source_text = build_source_text(sources)

    if source_text:
        answer = f"{answer}\n\n{source_text}"

    return {
        "answer": answer,
        "sources": sources,
        "context": context_parts,
    }