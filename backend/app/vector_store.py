import os


RETRIEVAL_MODE = os.environ.get("RETRIEVAL_MODE", "tfidf").lower()

if RETRIEVAL_MODE == "chroma":
    from app.chroma_store import add_chunks, search_chunks
else:
    from app.tfidf_store import add_chunks, search_chunks
