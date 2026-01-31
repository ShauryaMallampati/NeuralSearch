"""
Search functionality - find relevant chunks from queries
"""

import numpy as np
from typing import Optional

from .embedder import embed_query
from .storage import load_faiss_index, load_metadata, index_exists


def search(query: str, k: int = 5) -> Optional[list[dict]]:
    """
    search the index for chunks most similar to the query
    
    Args:
        query: The search query text
        k: Number of results to return
    
    Returns:
        List of result dicts with metadata + similarity scores,
        or None if index doesn't exist
    """
    if not index_exists():
        return None
    
    index = load_faiss_index()
    metadata = load_metadata()
    
    if index is None or metadata is None:
        return None
    
    # embed the query
    query_vector = embed_query(query)
    
    # reshape for FAISS (needs 2D array)
    query_vector = query_vector.reshape(1, -1).astype(np.float32)
    
    # search! returns distances and indices
    # since we use inner product with normalized vectors, higher = more similar
    scores, indices = index.search(query_vector, min(k, index.ntotal))
    
    # flatten results (they come as 2D arrays)
    scores = scores[0]
    indices = indices[0]
    
    # build result list
    results = []
    for score, idx in zip(scores, indices):
        if idx == -1:  # FAISS returns -1 for empty slots
            continue
        
        chunk_meta = metadata[idx].copy()
        chunk_meta["similarity_score"] = float(score)
        results.append(chunk_meta)
    
    return results


def format_citation(result: dict, include_pages: bool = True) -> str:
    """format a result as a citation string"""
    filename = result["file_name"]
    
    if include_pages:
        page_start = result["page_start"]
        page_end = result["page_end"]
        
        if page_start == page_end:
            return f"({filename}, p. {page_start})"
        else:
            return f"({filename}, p. {page_start}–{page_end})"
    
    return f"({filename})"


def highlight_keywords(text: str, query: str, 
                       highlight_start: str = "**", 
                       highlight_end: str = "**") -> str:
    """
    simple keyword highlighting - wraps query words found in text
    case-insensitive matching
    """
    # get meaningful words from query (skip tiny ones)
    query_words = [w.lower() for w in query.split() if len(w) > 2]
    
    if not query_words:
        return text
    
    # do this word by word to preserve original casing
    result_words = []
    for word in text.split():
        word_lower = word.lower().strip(".,!?;:\"'()[]")
        
        if word_lower in query_words:
            # wrap the word in highlights
            result_words.append(f"{highlight_start}{word}{highlight_end}")
        else:
            result_words.append(word)
    
    return " ".join(result_words)
