from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import rag
import rag_ramayana
import database

database.init_db()

app = FastAPI(title="Bhagavad Gita RAG MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None
    text_type: str = "GITA"

class CreateChatRequest(BaseModel):
    text_type: str = "GITA"

class ChatResponse(BaseModel):
    answer: str

@app.post("/api/chats")
async def create_chat_endpoint(req: CreateChatRequest = None):
    text_type = req.text_type if req else "GITA"
    chat_id = database.create_chat("New Chat", text_type)
    
    if text_type == "RAMAYANA":
        greeting = 'Welcome, seeker. I am an oracle of the Ramayana. How may its boundless wisdom guide you today?'
    else:
        greeting = 'O seeker of Truth, I am here to share the profound wisdom of the Bhagavad Gita. What queries burden your mind today?'
        
    database.add_message(chat_id, 'bot', greeting)
    return {"chat_id": chat_id, "text_type": text_type}

@app.get("/api/chats")
async def get_chats_endpoint():
    return database.get_chats()

@app.get("/api/chats/{chat_id}")
async def get_chat_history_endpoint(chat_id: str):
    return database.get_messages(chat_id)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    chat_id = request.chat_id
    if chat_id:
        database.add_message(chat_id, 'user', request.query)

    try:
        if request.text_type == "RAMAYANA":
            verses = rag_ramayana.retrieve_verses(request.query)
            answer = rag_ramayana.generate_answer(request.query, verses)
        else:
            verses = rag.retrieve_verses(request.query)
            answer = rag.generate_answer(request.query, verses)
        
        if chat_id:
            database.add_message(chat_id, 'bot', answer)
            
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
