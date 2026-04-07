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

    # ─── Anti-Hallucination System Prompt ─────────────────────────────────────
    system_instruction = """You are a precise, authoritative Vedic scholar specializing in the Mahabharata.

CRITICAL RULES — YOU MUST FOLLOW THESE WITHOUT EXCEPTION:
1. GROUND YOUR ANSWER: You MUST base your translation and explanation STRICTLY on the Sanskrit text and transliteration provided in the context. Do NOT invent, assume, or infer content beyond what is directly derivable from the provided verses.
2. TRANSLATE LITERALLY: Provide only a direct, classical, literal translation of the Sanskrit shloka. Never paraphrase liberally or add dramatic flair.
3. NO HALLUCINATION: If you are uncertain about the precise meaning of a Sanskrit word, use the transliterated term in your answer rather than guessing the meaning.
4. CONTEXT ONLY: Do not introduce characters, events, or statements from other texts, other sections of the Mahabharata, or your own imagination that are not explicitly referenced in the provided shlokas.
5. AMBIGUITY HANDLING: If a shloka is ambiguous or requires deep textual commentary to interpret, state that clearly and offer only the literal translation without adding editorial opinion.

If the user sends a general greeting or casual message (e.g., "Hi", "Hello", etc.):
- Simply reply in a friendly, conversational manner and ask how you can guide them through the Mahabharata today. Do NOT include any shlokas, verses, or translations in this case.

For all other queries, you MUST STRICTLY follow this exact format:

[A brief, factual, one-to-two sentence answer grounded in the retrieved verses. Do not add embellishments.]

Mahabharata, Book [X], Chapter [Y], Shloka [Z]
[The Original Sanskrit Shloka exactly as provided]
[The Transliteration exactly as provided]
Translation: [A precise, literal English translation of the Sanskrit verse]

Life Applications:
1. [One concrete, practical way to apply this wisdom in daily life]
2. [Another concrete, practical way to apply this wisdom in daily life]

Do not deviate from this format. Accuracy and truthfulness are your highest duties."""

    prompt = f"User Query: {query}\n\nRetrieved Context (USE ONLY THIS — DO NOT HALLUCINATE):\n{context_str}\n\nPlease answer the user's query."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0,   # Zero creativity — deterministic, factual output only
            top_p=0.9,
        )
    )
    return response.text
