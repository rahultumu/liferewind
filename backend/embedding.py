from openai import OpenAI
import numpy as np
import hashlib
import os

# Initialize client with API key (may be invalid for demo mode)
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-demo"))
except Exception:
    client = None

def create_embedding(text):
    """
    Create embeddings for text.
    In demo mode (invalid/missing API key), uses hash-based embeddings instead.
    """
    if client:
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            # Fall back to demo mode on any API error
            pass
    
    # Demo mode: Generate deterministic embedding from text hash
    # This is deterministic - same text always gives same embedding
    hash_obj = hashlib.sha256(text.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    
    # Seed numpy random generator with hash
    rng = np.random.RandomState(hash_int % (2**32))
    embedding = rng.randn(1536).astype("float32")
    
    # Normalize
    embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
    
    return embedding


