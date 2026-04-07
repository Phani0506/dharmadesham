import json
import os
import glob
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def format_verse(verse_data):
    book = verse_data.get("book", "")
    chapter = verse_data.get("chapter", "")
    shloka = verse_data.get("shloka", "")
    text = verse_data.get("text", "").strip()
    transliteration = verse_data.get("transliteration", "")
    if transliteration:
        transliteration = transliteration.strip()
    else:
        transliteration = ""
    
    formatted = f"Mahabharata Book {book} Chapter {chapter} Shloka {shloka}\n"
    formatted += f"Sanskrit Shloka: {text}\n"
    if transliteration:
        formatted += f"Transliteration: {transliteration}\n"
    return formatted

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mahabharata_dir = os.path.join(script_dir, "..", "mahabharata")
    json_patterns = glob.glob(os.path.join(mahabharata_dir, "*.json"))
    
    documents = []
    metadata = []
    
    for file_path in json_patterns:
        print(f"Loading {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print(f"Formatting {len(data)} verses from {os.path.basename(file_path)}...")
        for verse in data:
            doc_text = format_verse(verse)
            documents.append(doc_text)
            metadata.append({
                "book": verse.get("book"),
                "chapter": verse.get("chapter"),
                "shloka_num": verse.get("shloka"),
                "text": verse.get("text", "") or "",
                "transliteration": verse.get("transliteration", "") or "",
                "meaning": "", # Not available, to be generated dynamically
                "explanation": "" # Not available, to be generated dynamically
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
    out_dir = script_dir  # save next to ingest_mahabharata.py i.e. backend/
    faiss.write_index(index, os.path.join(out_dir, "mahabharata.index"))
    with open(os.path.join(out_dir, "mahabharata_meta.pkl"), "wb") as f:
        pickle.dump(metadata, f)
        
    print("Done! Mahabharata RAG database is ready.")

if __name__ == "__main__":
    main()
