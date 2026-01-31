"""
Embedding module - converts text to meaning vectors
all local, no APIs, totally offline
"""

import numpy as np
from functools import lru_cache
from sentence_transformers import SentenceTransformer

# small but mighty model that actually works great
MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """
    load the embedding model (cached so we only do this once)
    first load takes a few seconds, then it's instant
    """
    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded!")
    return model


def embed_texts(texts: list[str], batch_size: int = 32, 
                show_progress: bool = False) -> np.ndarray:
    """
    embed a list of texts into vectors
    
    Args:
        texts: List of strings to embed
        batch_size: How many to process at once (memory management)
        show_progress: Show a progress bar (useful for large batches)
    
    Returns:
        numpy array of shape (len(texts), embedding_dim)
        Vectors are L2 normalized for cosine similarity
    """
    model = get_model()
    
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True  # Important for cosine similarity!
    )
    
    return embeddings


def embed_query(query: str) -> np.ndarray:
    """
    embed a single search query
    returns a 1D normalized vector
    """
    model = get_model()
    
    embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    return embedding


def get_embedding_dim() -> int:
    """get the dimensionality of our embeddings"""
    model = get_model()
    return model.get_sentence_embedding_dimension()
