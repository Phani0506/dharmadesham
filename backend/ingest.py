import json
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def format_verse(verse_data):
    text = verse_data.get("text", "").strip()
    transliteration = verse_data.get("transliteration", "").strip()
    meaning = verse_data.get("word_meanings", "").strip()
    
    formatted = f"Bhagavad Gita Chapter {verse_data.get('chapter_number')} Verse {verse_data.get('verse_number')}\n"
    formatted += f"Sanskrit Shloka: {text}\n"
    formatted += f"Transliteration: {transliteration}\n"
    formatted += f"Meaning/Translation: {meaning}\n"
    return formatted

def main():
    print("Loading gita.json...")
    with open("../gita.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    documents = []
    metadata = []
    
    print("Formatting verses...")
    for verse in data:
        doc_text = format_verse(verse)
        documents.append(doc_text)
        metadata.append({
            "chapter_number": verse.get("chapter_number"),
            "verse_number": verse.get("verse_number"),
            "text": verse.get("text", "").strip(),
            "transliteration": verse.get("transliteration", "").strip(),
            "meaning": verse.get("word_meanings", "").strip()
        })
        
    print(f"Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Generating embeddings for {len(documents)} verses (offline & free)...")
    embeddings_np = model.encode(documents, show_progress_bar=True, convert_to_numpy=True)
    embeddings_np = np.array(embeddings_np).astype('float32')
    
    print("Building FAISS index...")
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    
    print("Saving index and metadata...")
    faiss.write_index(index, "gita.index")
    with open("gita_meta.pkl", "wb") as f:
        pickle.dump(metadata, f)
        
    print("Done! RAG database is ready.")

if __name__ == "__main__":
    main()
