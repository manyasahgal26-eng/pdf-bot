from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.document_loader import load_document
from app.chunker import chunk_pages
from app.vector_store import add_chunks, search_chunks
from app.rag import answer_question


app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class ChatRequest(BaseModel):
    question: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "RAG bot backend running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = load_document(str(file_path))
    chunks = chunk_pages(pages)
    stored_chunks = add_chunks(chunks, file.filename)

    return {
        "filename": file.filename,
        "pages_found": len(pages),
        "chunks_found": len(chunks),
        "stored_chunks": stored_chunks,
        "preview": chunks[:3],
    }


@app.get("/search")
def search(question: str):
    matches = search_chunks(question)

    return {
        "question": question,
        "matches": matches,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    result = answer_question(request.question)

    return {
        "question": request.question,
        **result,
    }