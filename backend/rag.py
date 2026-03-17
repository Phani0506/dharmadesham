import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if API_KEY and API_KEY != "YOUR_API_KEY_HERE":
    client = genai.Client(api_key=API_KEY)

_index = None
_metadata = None
_embed_model = None

def load_data():
    global _index, _metadata, _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    if _index is None:
        if os.path.exists("gita.index"):
            _index = faiss.read_index("gita.index")
        else:
            raise Exception("FAISS index not found. Run ingest.py first.")
            
    if _metadata is None:
        if os.path.exists("gita_meta.pkl"):
            with open("gita_meta.pkl", "rb") as f:
                _metadata = pickle.load(f)
        else:
            raise Exception("Metadata not found. Run ingest.py first.")

def retrieve_verses(query: str, top_k: int = 3):
    load_data()
    
    query_embedding = _embed_model.encode([query], convert_to_numpy=True)
    query_embedding = np.array(query_embedding).astype('float32')
    
    distances, indices = _index.search(query_embedding, top_k)
    
    results = []
    for idx in indices[0]:
        if idx >= 0 and idx < len(_metadata):
            results.append(_metadata[idx])
            
    return results

def generate_answer(query: str, retrieved_verses: list):
    context_str = ""
    for i, v in enumerate(retrieved_verses):
        context_str += f"--- Verse {i+1} ---\n"
        context_str += f"Chapter: {v.get('chapter_number')}, Verse: {v.get('verse_number')}\n"
        context_str += f"Sanskrit: {v.get('text')}\n"
        context_str += f"Transliteration: {v.get('transliteration')}\n"
        context_str += f"Translation/Meaning: {v.get('meaning')}\n\n"
        
    system_instruction = """You are a polite, authoritative Vedic scholar.
Your task is to answer user questions about the Bhagavad Gita based ONLY on the provided retrieved verses.
You must STRICTLY follow this exact formatting in your response:

[Your direct, conversational, insightful answer to the user's question]

Chapter [X], Verse [Y]
[The Original Sanskrit Shloka]
[The Translation/Meaning]

[Provide 2-3 highly actionable, modern-day steps the user can take today to apply this wisdom to their daily life, career, or relationships.]

Do not deviate from this format. Emulate a wise scholar."""

    prompt = f"User Query: {query}\n\nRetrieved Context:\n{context_str}\n\nPlease answer the user's query."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
        )
    )
    return response.text
