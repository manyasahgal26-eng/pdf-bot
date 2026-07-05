from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from app.tts import text_to_speech

from app.document_loader import load_document
from app.chunker import chunk_pages
from app.vector_store import add_chunks, search_chunks
from app.rag import answer_question
from app.keyword_extractor import extract_document_terms, save_document_terms


app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class ChatRequest(BaseModel):
    question: str
    use_web: bool = False
    language: str = "english"
    filename: str = None


class TTSRequest(BaseModel):
    text: str
    language: str = "english"


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

    terms = extract_document_terms(chunks)
    save_document_terms(file.filename, terms)

    stored_chunks = add_chunks(chunks, file.filename)

    return {
        "filename": file.filename,
        "pages_found": len(pages),
        "chunks_found": len(chunks),
        "stored_chunks": stored_chunks,
        "terms_found": len(terms),
        "preview": chunks[:3],
    }
@app.post("/text-to-speech")
async def create_speech(request: TTSRequest):
    audio_path = await text_to_speech(
        text=request.text,
        language=request.language,
    )

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename="answer.mp3",
    )

@app.get("/search")
def search(question: str):
    matches = search_chunks(question)

    return {
        "question": question,
        "matches": matches,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    result = answer_question(
        question=request.question,
        use_web=request.use_web,
        language=request.language,
        filename=request.filename,
    )

    return {
        "question": request.question,
        "use_web": request.use_web,
        "language": request.language,
        "filename": request.filename,
        **result,
    }
