"""
Chunking logic - splits documents into searchable pieces
overlapping them so we don't lose context at the edges
"""

import hashlib
from typing import Generator


# Config - about 300 words per chunk with 50 word overlap
# that's roughly 400 tokens which works great with embedding models
CHUNK_SIZE_WORDS = 300
CHUNK_OVERLAP_WORDS = 50


def generate_doc_id(filename: str) -> str:
    """generate a stable ID from the filename"""
    return hashlib.md5(filename.encode()).hexdigest()[:12]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_WORDS, 
               overlap: int = CHUNK_OVERLAP_WORDS) -> Generator[str, None, None]:
    """
    split text into overlapping chunks based on word count
    yields chunk strings
    """
    words = text.split()
    
    if len(words) <= chunk_size:
        # text is short enough, just one chunk
        yield text
        return
    
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        yield " ".join(chunk_words)
        
        # move forward by (chunk_size - overlap)
        start += chunk_size - overlap
        
        # if what's left is smaller than overlap, stop
        if start >= len(words):
            break


def create_chunks_with_metadata(doc_pages: list[dict], filename: str) -> list[dict]:
    """
    create chunks from document pages, keeping page number info
    
    Args:
        doc_pages: List of {"page_num": int, "text": str}
        filename: Original filename
    
    Returns:
        List of chunk metadata dicts ready for indexing
    """
    doc_id = generate_doc_id(filename)
    chunks = []
    chunk_counter = 0
    
    # combine all text with page markers
    # so we can chunk across page boundaries smoothly
    combined_parts = []
    for page in doc_pages:
        words = page["text"].split()
        for word in words:
            combined_parts.append({
                "word": word,
                "page": page["page_num"]
            })
    
    if not combined_parts:
        return []
    
    # now chunk through the combined text
    start_idx = 0
    
    while start_idx < len(combined_parts):
        end_idx = min(start_idx + CHUNK_SIZE_WORDS, len(combined_parts))
        
        chunk_parts = combined_parts[start_idx:end_idx]
        chunk_text = " ".join(p["word"] for p in chunk_parts)
        
        # figure out which pages this chunk spans
        pages_in_chunk = sorted(set(p["page"] for p in chunk_parts))
        page_start = pages_in_chunk[0]
        page_end = pages_in_chunk[-1]
        
        chunks.append({
            "doc_id": doc_id,
            "file_name": filename,
            "chunk_id": f"{doc_id}_{chunk_counter}",
            "page_start": page_start,
            "page_end": page_end,
            "text": chunk_text
        })
        
        chunk_counter += 1
        start_idx += CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS
        
        if start_idx >= len(combined_parts):
            break
    
    return chunks


def process_all_documents(docs_by_file: dict[str, list[dict]]) -> list[dict]:
    """
    process multiple documents into chunks
    
    Args:
        docs_by_file: Dict mapping filename -> list of page dicts
    
    Returns:
        Flat list of all chunk metadata
    """
    all_chunks = []
    
    for filename, pages in docs_by_file.items():
        chunks = create_chunks_with_metadata(pages, filename)
        all_chunks.extend(chunks)
    
    return all_chunks
