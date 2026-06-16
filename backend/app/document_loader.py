from pathlib import Path

from docx import Document
from pypdf import PdfReader


def load_pdf(file_path: str) -> list[dict]:
    reader = PdfReader(file_path)
    pages = []

    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()

        if text:
            pages.append({
                "page": index + 1,
                "text": text,
            })

    return pages


def load_docx(file_path: str) -> list[dict]:
    document = Document(file_path)
    text_parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            text_parts.append(text)

    full_text = "\n".join(text_parts)

    if not full_text:
        return []

    return [{
        "page": 1,
        "text": full_text,
    }]


def load_document(file_path: str) -> list[dict]:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return load_pdf(file_path)

    if suffix == ".docx":
        return load_docx(file_path)

    raise ValueError(f"Unsupported file type: {suffix}")