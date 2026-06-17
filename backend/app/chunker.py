def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

    return chunks


def chunk_pages(pages: list[dict]) -> list[dict]:
    all_chunks = []

    for page in pages:
        page_number = page["page"]
        text = page["text"]

        page_chunks = chunk_text(text)

        for index, chunk in enumerate(page_chunks):
            all_chunks.append({
                "id": f"page-{page_number}-chunk-{index + 1}",
                "page": page_number,
                "chunk_index": index + 1,
                "text": chunk,
            })

    return all_chunks