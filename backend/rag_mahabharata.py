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

MODEL_FALLBACK = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-001",
]

def generate_with_fallback(prompt: str, system_instruction: str, config_kwargs: dict = None):
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
                continue
            raise
    raise Exception("All Gemini models are currently rate-limited. Please wait a minute and try again.")

_index = None
_metadata = None
_embed_model = None

def load_data():
    global _index, _metadata, _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    if _index is None:
        if os.path.exists("mahabharata.index"):
            _index = faiss.read_index("mahabharata.index")
        else:
            raise Exception("FAISS index not found. Run ingest_mahabharata.py first.")
            
    if _metadata is None:
        if os.path.exists("mahabharata_meta.pkl"):
            with open("mahabharata_meta.pkl", "rb") as f:
                _metadata = pickle.load(f)
        else:
            raise Exception("Metadata not found. Run ingest_mahabharata.py first.")

def retrieve_verses(query: str, top_k: int = 5):
    """Retrieves top_k most relevant verses. Higher top_k grounds the LLM better."""
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
        context_str += f"Book: {v.get('book')}, Chapter: {v.get('chapter')}, Shloka: {v.get('shloka_num')}\n"
        context_str += f"Sanskrit: {v.get('text')}\n"
        context_str += f"Transliteration: {v.get('transliteration')}\n\n"

    # ─── Scholarly & Wise System Prompt ─────────────────────────────────────
    system_instruction = """You are a wise and authoritative Vedic scholar specializing in the Mahabharata.
Your duty is to illuminate the profound wisdom of the Mahabharata for the user.

GUIDELINES FOR YOUR WISDOM:
1. HOLISTIC UNDERSTANDING: Use the provided retrieved verses as your primary foundation. However, as a master scholar, you may use your internal knowledge of the Mahabharata to weave a coherent, philosophical, and logical answer that addresses the user's query directly.
2. SCHOLARLY TONE: Speak with the grace, depth, and clarity of a wise oracle. Your words should inspire and educate.
3. HANDLING GAPS: If the retrieved verses do not perfectly answer the query, find the closest philosophical connection. Explain the broader principle (Dharma, Karma, Duty, etc.) that the verses represent and how it answers the user's intent.
4. DO NOT SAY "NOT DIRECTLY ADDRESSED": Your goal is to guide the user. Avoid rejecting queries unless they are completely unrelated to Indian epics. Even then, try to pivot to a relevant Mahabharata teaching.

If the user sends a general greeting or casual message (e.g., "Hi", "Hello", etc.):
- Simply reply in a friendly, conversational manner and ask how you can guide them through the secrets of the Mahabharata today. Do NOT include any shlokas or translations.

For all other queries, you must STRICTLY follow this exact format:

[A profound, logical, and scholarly answer to the query (2-4 sentences). Ground this in the retrieved context but ensure it flows naturally.]

Mahabharata, Book [X], Chapter [Y], Shloka [Z]
[The Original Sanskrit Shloka from the most relevant retrieved verse]
[The Transliteration from the same most relevant verse]
Translation: [A precise, meaningful English translation of the Sanskrit verse provided above]

Life Applications:
1. [A concrete, practical way to apply this wisdom in modern daily life]
2. [Another concrete, practical way to apply this wisdom in modern daily life]

Accuracy to the spirit of the Mahabharata is your highest duty."""

    prompt = f"User Query: {query}\n\nRetrieved Context (foundation for your answer):\n{context_str}\n\nPlease provide your scholarly guidance."
    
    return generate_with_fallback(prompt, system_instruction, {"temperature": 0.3, "top_p": 0.95})

