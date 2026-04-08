import os
import pickle
import time
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

# Models to try in order — fallback automatically if one is rate-limited
MODEL_FALLBACK = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-001",
]

def generate_with_fallback(prompt: str, system_instruction: str, config_kwargs: dict = None):
    """Try each model in order; return first successful response."""
    for model in MODEL_FALLBACK:
        try:
            cfg = genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                **(config_kwargs or {})
            )
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=cfg,
            )
            return response.text
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err or "UNAVAILABLE" in err or "EXHAUSTED" in err:
                time.sleep(1)
                continue  # try next model
            raise  # re-raise unexpected errors
    raise Exception("All Gemini models are currently rate-limited. Please wait a minute and try again.")

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

def retrieve_verses(query: str, top_k: int = 2):
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

If the user sends a general greeting or casual message (e.g., "Hi", "Hello", etc.):
- Simply reply in a friendly, conversational manner and ask how you can act as a guide for them today. Do NOT include any slokas, verses, or translations in this case.

For all other queries, you must STRICTLY follow this exact formatting in your response:

[A philosophical and logical answer to the user's question. Keep this answer short, strictly about two lines maximum.]

Chapter [X], Verse [Y]
[The Original Sanskrit Shloka]
[The Translation/Meaning]

[Provide exactly 2 ways how the user can implement this wisdom in their daily life.]

Do not deviate from this format. Emulate a wise scholar."""

    prompt = f"User Query: {query}\n\nRetrieved Context:\n{context_str}\n\nPlease answer the user's query."
    
    return generate_with_fallback(prompt, system_instruction)
