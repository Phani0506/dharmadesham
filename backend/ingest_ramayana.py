import json
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def format_verse(verse_data):
    kanda = verse_data.get("kanda", "")
    sarga = verse_data.get("sarga", "")
    shloka = verse_data.get("shloka", "")
    text = verse_data.get("shloka_text", "").strip()
    transliteration = verse_data.get("transliteration", "")
    if transliteration:
        transliteration = transliteration.strip()
    else:
        transliteration = ""
        
    translation = verse_data.get("translation", "")
    if translation: translation = translation.strip()
    else: translation = ""
    
    explanation = verse_data.get("explanation", "")
    if explanation: explanation = explanation.strip()
    else: explanation = ""
    
    formatted = f"Ramayana {kanda} Sarga {sarga} Shloka {shloka}\n"
    formatted += f"Sanskrit Shloka: {text}\n"
    if transliteration:
        formatted += f"Transliteration: {transliteration}\n"
    formatted += f"Meaning/Translation: {translation}\n"
    formatted += f"Explanation: {explanation}\n"
    return formatted

def main():
    print("Loading ramayana.json...")
    with open("../ramayana.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    documents = []
    metadata = []
    
    print("Formatting verses...")
    for verse in data:
        doc_text = format_verse(verse)
        documents.append(doc_text)
        metadata.append({
            "kanda": verse.get("kanda"),
            "sarga": verse.get("sarga"),
            "shloka_num": verse.get("shloka"),
            "text": verse.get("shloka_text", "") or "",
            "transliteration": verse.get("transliteration", "") or "",
            "meaning": verse.get("translation", "") or "",
            "explanation": verse.get("explanation", "") or ""
        })
        
    print(f"Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Generating embeddings for {len(documents)} verses (this will take a few minutes)...")
    embeddings_np = model.encode(documents, show_progress_bar=True, convert_to_numpy=True)
    embeddings_np = np.array(embeddings_np).astype('float32')
    
    print("Building FAISS index...")
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    
    print("Saving index and metadata...")
    faiss.write_index(index, "ramayana.index")
    with open("ramayana_meta.pkl", "wb") as f:
        pickle.dump(metadata, f)
        
    print("Done! Ramayana RAG database is ready.")

if __name__ == "__main__":
    main()
