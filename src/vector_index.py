"""
FAISS vector index management
building, saving, and loading the search index
"""

import faiss
import numpy as np
from typing import Optional

from .embedder import embed_texts, get_embedding_dim
from .storage import save_faiss_index, save_metadata, load_faiss_index, load_metadata


def build_index(chunks: list[dict], progress_callback=None) -> tuple[faiss.Index, list[dict]]:
    """
    build a FAISS index from chunk metadata
    
    Args:
        chunks: List of chunk dicts (must have 'text' field)
        progress_callback: Optional callback(current, total) for progress updates
    
    Returns:
        (faiss_index, metadata_list)
    """
    if not chunks:
        raise ValueError("No chunks to index!")
    
    texts = [c["text"] for c in chunks]
    total = len(texts)
    
    if progress_callback:
        progress_callback(0, total)
    
    # embed all the chunks - this is the slow part
    print(f"Embedding {total} chunks...")
    embeddings = embed_texts(texts, show_progress=True)
    
    if progress_callback:
        progress_callback(total // 2, total)
    
    # build FAISS index
    # using IndexFlatIP (inner product) because our vectors are normalized
    # inner product of normalized vectors = cosine similarity
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    
    # add vectors to index
    index.add(embeddings.astype(np.float32))
    
    if progress_callback:
        progress_callback(total, total)
    
    print(f"Index built: {index.ntotal} vectors, dim={dim}")
    
    return index, chunks


def save_index_and_metadata(index: faiss.Index, metadata: list[dict]):
    """save the FAISS index and metadata to disk"""
    save_faiss_index(index)
    save_metadata(metadata)
    print("Index and metadata saved!")


def load_index_and_metadata() -> Optional[tuple[faiss.Index, list[dict]]]:
    """
    load the index and metadata from disk
    returns None if either doesn't exist
    """
    index = load_faiss_index()
    metadata = load_metadata()
    
    if index is None or metadata is None:
        return None
    
    return index, metadata


def add_to_index(index: faiss.Index, new_chunks: list[dict], 
                 existing_metadata: list[dict]) -> tuple[faiss.Index, list[dict]]:
    """
    add new chunks to an existing index
    returns the updated index and metadata
    
    Note: For simplicity, we rebuild from scratch. FAISS IndexFlatIP supports
    incremental adds, but managing metadata alignment gets messy.
    For a small-medium knowledge base, rebuild is fast enough.
    """
    all_chunks = existing_metadata + new_chunks
    return build_index(all_chunks)
