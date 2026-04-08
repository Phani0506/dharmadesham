import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

def test_search():
    base_path = r"c:\PHANI PERSONAL\PHANI PERSONAL 1\dharmadesham\backend"
    index_path = os.path.join(base_path, "mahabharata.index")
    meta_path = os.path.join(base_path, "mahabharata_meta.pkl")
    
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        print("Index files not found in CWD.")
        return

    print("Loading index and metadata...")
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)

    print(f"Index size: {index.ntotal}")
    print(f"Metadata size: {len(metadata)}")

    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    query = "What happens in the Sauptika Parva?" # This is Chapter 10
    print(f"Searching for: {query}")
    
    query_embedding = model.encode([query], convert_to_numpy=True)
    query_embedding = np.array(query_embedding).astype('float32')
    
    distances, indices = index.search(query_embedding, 5)
    
    for i, idx in enumerate(indices[0]):
        if idx >= 0:
            v = metadata[idx]
            print(f"\nResult {i+1}:")
            print(f"Book: {v.get('book')}, Chapter: {v.get('chapter')}, Shloka: {v.get('shloka_num')}")
            print(f"Sanskrit: {v.get('text')[:100]}...")

if __name__ == "__main__":
    test_search()
