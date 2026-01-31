"""
Storage utilities - handles all file I/O
keeps path logic in one place so it's not scattered everywhere
"""

import os
import json
from pathlib import Path
from typing import Optional
import faiss
import numpy as np

# Base paths - relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
INDEX_DIR = PROJECT_ROOT / "index"

FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.json"


def ensure_dirs():
    """create our directories if they don't exist. no big deal"""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file) -> Path:
    """
    save an uploaded file-like object to the uploads folder
    returns the path where it ended up
    """
    ensure_dirs()
    dest = UPLOADS_DIR / Path(uploaded_file.name).name
    with open(dest, "wb") as f:
        f.write(uploaded_file.read())
    return dest


def save_uploaded_path(file_path: str | Path) -> Path:
    """
    save an uploaded file from a temporary path to the uploads folder
    returns the path where it ended up
    """
    ensure_dirs()
    src = Path(file_path)
    dest = UPLOADS_DIR / src.name
    dest.write_bytes(src.read_bytes())
    return dest


def list_uploaded_pdfs() -> list[Path]:
    """get all PDFs that are sitting in the uploads folder"""
    ensure_dirs()
    return sorted(UPLOADS_DIR.glob("*.pdf"))


def delete_uploaded_file(filename: str) -> bool:
    """delete a PDF from uploads. returns True if it worked"""
    filepath = UPLOADS_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return True
    return False


def save_metadata(metadata: list[dict]):
    """dump chunk metadata to JSON"""
    ensure_dirs()
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def load_metadata() -> Optional[list[dict]]:
    """load chunk metadata from JSON. returns None if it doesn't exist"""
    if not METADATA_PATH.exists():
        return None
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_faiss_index(index: faiss.Index):
    """write the FAISS index to disk"""
    ensure_dirs()
    faiss.write_index(index, str(FAISS_INDEX_PATH))


def load_faiss_index() -> Optional[faiss.Index]:
    """read the FAISS index from disk. returns None if it doesn't exist"""
    if not FAISS_INDEX_PATH.exists():
        return None
    return faiss.read_index(str(FAISS_INDEX_PATH))


def index_exists() -> bool:
    """check if we have a built index ready to search"""
    return FAISS_INDEX_PATH.exists() and METADATA_PATH.exists()


def clear_index():
    """nuke the index files (uploads stay safe though)"""
    if FAISS_INDEX_PATH.exists():
        FAISS_INDEX_PATH.unlink()
    if METADATA_PATH.exists():
        METADATA_PATH.unlink()


def get_index_stats() -> Optional[dict]:
    """grab some basic stats about the current index"""
    if not index_exists():
        return None
    
    metadata = load_metadata()
    index = load_faiss_index()
    
    # Count unique docs
    unique_docs = set(m["file_name"] for m in metadata)
    
    # Get file size
    index_size_bytes = FAISS_INDEX_PATH.stat().st_size
    if index_size_bytes < 1024:
        size_str = f"{index_size_bytes} B"
    elif index_size_bytes < 1024 * 1024:
        size_str = f"{index_size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{index_size_bytes / (1024*1024):.2f} MB"
    
    return {
        "total_chunks": len(metadata),
        "total_docs": len(unique_docs),
        "doc_names": list(unique_docs),
        "embedding_dim": index.d,
        "index_size": size_str,
    }
