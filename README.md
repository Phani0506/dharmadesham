# Dharmadesham: Bhagavad Gita RAG MVP

A full-stack MVP application that allows users to ask questions about the Bhagavad Gita. This project uses a locally run Retrieval-Augmented Generation (RAG) pipeline to provide accurate, culturally authentic, and context-aware answers.

## Tech Stack
* **Frontend**: React, Vite, Tailwind/Vanilla CSS (Glassmorphism UI)
* **Backend**: Python, FastAPI
* **AI/RAG Layer**: 
  * **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`) run locally for free and unlimited rate limits.
  * **Vector Database**: FAISS (Facebook AI Similarity Search)
  * **LLM**: Google Gemini (`gemini-2.5-flash`) via the `google-genai` SDK.

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Node.js & npm

### 2. Backend Setup
Navigate to the backend directory and set up the virtual environment:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

**Environment Variables**:
Create a `.env` file in the `backend/` directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

**Data Ingestion**:
Ensure `gita.json` is in the root directory (outside `backend/`). Then run the ingestion script to build the vector index:
```bash
python ingest.py
```
*(This only needs to be run once to generate `gita.index` and `gita_meta.pkl`)*

### 3. Frontend Setup
Navigate to the frontend directory:
```bash
cd frontend
npm install
```

---

## 🚀 How to Run Locally

You need two terminal windows to run both the backend API and the frontend UI.

### Terminal 1: Start the Backend (FastAPI)
```bash
cd backend
.\venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```
*The API will run at `http://localhost:8000` (and `0.0.0.0:8000` for your local network).*

### Terminal 2: Start the Frontend (React/Vite)
```bash
cd frontend
npm run dev
```
*The UI will run at `http://localhost:5173`. Because Vite is configured with `--host`, you can also access it via your Local IPv4 address (e.g., `http://192.168.x.x:5173`) from your phone or other devices on the same Wi-Fi network.*
