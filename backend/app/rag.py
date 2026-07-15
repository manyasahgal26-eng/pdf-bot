from app.llm import generate_answer, rewrite_query_for_search, classify_query, generate_computation_answer, generate_web_answer
from app.vector_store import search_chunks
from app.web_search import get_web_context


def is_question_bank_chunk(text: str) -> bool:
    text_lower = text.lower()

    repeated_question_phrases = (
        text_lower.count("explain the concept")
        + text_lower.count("with example")
        + text_lower.count("in operating system")
    )

    numbered_items = sum(
        1
        for token in text_lower.replace("\n", " ").split()
        if token.rstrip(".").isdigit()
    )

    return repeated_question_phrases >= 6 or numbered_items >= 18


def rerank_matches(question: str, matches: list[dict]) -> list[dict]:
    query_terms = [
        term
        for term in question.lower().replace("-", " ").split()
        if len(term) > 2
    ]

    scored_matches = []

    for match in matches:
        text = match["text"]
        text_lower = text.lower()

        if is_question_bank_chunk(text):
            continue

        score = 0.0

        for term in query_terms:
            score += text_lower.count(term) * 4

        if any(cue in text_lower for cue in [" is a ", " refers to ", " is used ", " used to "]):
            score += 8

        if any(cue in text_lower for cue in ["controls", "synchronization", "mutual exclusion", "shared"]):
            score += 4

        distance = match.get("distance")
        if isinstance(distance, (int, float)):
            score -= distance * 0.05

        scored_matches.append((score, match))

    if not scored_matches:
        return matches[:4]

    scored_matches.sort(key=lambda item: item[0], reverse=True)
    return [match for score, match in scored_matches[:4]]


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


def build_source_text(sources: list[dict]) -> str:
    if not sources:
        return ""

    best_source = sources[0]
    page = best_source.get("page", "unknown")

    return f"Page {page}"


def build_document_context(matches: list[dict]) -> str:
    context_parts = []

    for index, match in enumerate(matches, start=1):
        metadata = match["metadata"]
        filename = metadata.get("filename", "uploaded document")
        page = metadata.get("page", "unknown")
        text = match["text"]

        context_parts.append(
            f"[DOC {index} | {filename}, page {page}]\n{text}"
        )

    return "\n\n".join(context_parts)


def answer_question(
    question: str,
    use_web: bool = False,
    language: str = "auto",
    filename: str = None,
) -> dict:
    # 1. Classify the query intent
    routing_decision = classify_query(question)

    if routing_decision == "computation":
        answer = generate_computation_answer(question)
        return {
            "answer": answer,
            "sources": [],
            "web_sources": [],
            "context": [],
            "routing_decision": "computation",
        }

    elif routing_decision == "web_search":
        web_result = get_web_context(question)
        web_context = web_result["context"]
        web_sources = web_result["sources"]

        if not web_context:
            answer = "I could not find this in the uploaded document or reliable web sources."
        else:
            answer = generate_web_answer(question, web_context, language)

        return {
            "answer": answer,
            "sources": [],
            "web_sources": web_sources,
            "context": [],
            "routing_decision": "web_search",
        }

    else:
        # Document Retrieval Route (Default)
        search_query = rewrite_query_for_search(question)
        raw_matches = search_chunks(search_query, filename=filename, top_k=12)
        matches = rerank_matches(search_query, raw_matches)

        document_context = build_document_context(matches)
        document_context_parts = [match["text"] for match in matches]
        document_sources = format_sources(matches)

        web_context = ""
        web_sources = []

        if use_web:
            web_result = get_web_context(question)
            web_context = web_result["context"]
            web_sources = web_result["sources"]

        if not document_context and not web_context:
            return {
                "answer": "I could not find this in the uploaded document or reliable web sources.",
                "sources": [],
                "web_sources": [],
                "context": [],
                "routing_decision": "document_retrieval",
            }

        combined_context = ""

        if document_context:
            combined_context += f"Uploaded document context:\n{document_context}\n\n"

        if web_context:
            combined_context += f"Web context:\n{web_context}\n\n"

        answer = generate_answer(question, combined_context, language)
        source_text = build_source_text(document_sources)

        if (
            source_text
            and "I could not find this" not in answer
            and source_text not in answer
        ):
            answer = f"{answer}\n\n{source_text}"

        return {
            "answer": answer,
            "sources": document_sources,
            "web_sources": web_sources,
            "context": document_context_parts,
            "routing_decision": "document_retrieval",
        }

