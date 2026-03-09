import faiss
import numpy as np
import pickle
import json
from pathlib import Path

dimension = 1536
INDEX_PATH = "vector_db/faiss_index.bin"
MEMORIES_PATH = "vector_db/memories.json"

# Create vector_db directory if it doesn't exist
Path("vector_db").mkdir(exist_ok=True)

# Load or create index
def load_index():
    global index, memory_texts
    
    if Path(INDEX_PATH).exists():
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(dimension)
    
    # Load memory texts
    if Path(MEMORIES_PATH).exists():
        with open(MEMORIES_PATH, "r") as f:
            memory_texts = json.load(f)
    else:
        memory_texts = []

# Initialize on module load
index = faiss.IndexFlatL2(dimension)
memory_texts = []
load_index()

def save_index():
    """Save FAISS index and memory texts to disk"""
    try:
        faiss.write_index(index, INDEX_PATH)
        with open(MEMORIES_PATH, "w") as f:
            json.dump(memory_texts, f, indent=2)
    except Exception as e:
        print(f"Error saving index: {e}")

def add_memory(embedding, text):
    global index, memory_texts
    
    index.add(np.array([embedding]).astype("float32"))
    memory_texts.append(text)
    
    # Save to disk immediately
    save_index()

def search_memory(query_embedding, k=3):

    D, I = index.search(np.array([query_embedding]).astype("float32"), k)

    results = []

    for i in I[0]:
        if i < len(memory_texts):
            results.append(memory_texts[i])

    return results
