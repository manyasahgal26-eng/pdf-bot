DocuRAG 

DocuRAG is a modern, responsive document-based Question-Answering (RAG) system. It allows users to upload PDF or DOCX documents, automatically index them, and ask questions through an interactive chat interface. 

The system features session-based document isolation, local caching to prevent data loss on server restarts, multilingual support, web-search fallback, and Text-to-Speech (TTS) audio answers.



Live Demo & Deployment
* **Live Web App (Frontend):https://docurag-blue.vercel.app/ 
  Backend API Server:https://docurag-backend.onrender.com/

 Features

- **Isolated Sessions:** Different users chatting from different devices get isolated document contexts. There is no mixing of document contents or chats.
- **Data Persistence:** Chunk indexes are cached locally on disk (`data/chunks/`). If the server goes to sleep (e.g. Render Free Tier) or restarts, document data is automatically reloaded on demand without requiring re-upload.
- **Multilingual QA:** Answer questions in English, Hindi, Hinglish, French, Spanish, Punjabi, or Roman Punjabi.
- **Text-to-Speech (TTS):** Integrated audio player to listen to generated answers using natural voices.
- **Dual Search Engine:**
  - **TF-IDF (Default):** Ultra-lightweight and fast, optimized for memory-restricted free hosting platforms.
  - **Chroma Mode:** High-quality semantic vector search powered by `sentence-transformers` and `ChromaDB`.
- **Web Search Integration:** Fallback to DuckDuckGo search to support document information with web results when needed.

---

## Architecture & Tech Stack

- **Frontend:** React, Vite, Lucide Icons, Vanilla CSS
- **Backend:** FastAPI (Python), PyPDF, Python-Docx, Scikit-Learn, ChromaDB
- **LLM Engine:** Groq API (`llama-3.3-70b-versatile` model)
- **TTS Engine:** Edge-TTS

---

## Local Setup & Installation

### Prerequisite
Make sure you have **Node.js** (v18+) and **Python** (3.10+) installed.

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   * **For TF-IDF mode (Lightweight):**
     ```bash
     pip install -r requirements.txt
     ```
   * **For Chroma mode (Semantic embeddings):**
     ```bash
     pip install -r requirements-chroma.txt
     ```
4. Create a `.env` file in the `backend/` folder and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   RETRIEVAL_MODE=tfidf  # or 'chroma'
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
   The backend will be running at `http://127.0.0.1:8000`.

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file (optional if running locally on port 8000) or configure the base URL:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```
4. Run the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173` (or `http://localhost:5174` if 5173 is in use).

---

 Supported Formats
* **PDF** (`.pdf`)
* **Word Documents** (`.docx`)
