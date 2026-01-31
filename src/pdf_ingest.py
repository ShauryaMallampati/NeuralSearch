"""
PDF ingestion - reads PDFs page by page
straightforward stuff, nothing fancy
"""

from pathlib import Path
from pypdf import PdfReader


def extract_text_by_page(pdf_path: Path) -> list[dict]:
    """
    extract text from a PDF, keeping track of page numbers
    
    returns list of dicts like:
    [{"page_num": 1, "text": "..."}, {"page_num": 2, "text": "..."}, ...]
    
    page numbers start at 1 because that's what makes sense to humans
    """
    pages = []
    
    try:
        reader = PdfReader(pdf_path)
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            # clean it up a bit
            text = text.strip()
            
            if text:  # only add pages with actual content
                pages.append({
                    "page_num": i + 1,  # 1-indexed like normal people expect
                    "text": text
                })
        
    except Exception as e:
        # stuff breaks sometimes with weird PDFs, just log it and keep going
        print(f"couldn't read {pdf_path.name}: {e}")
    
    return pages
    
    return pages


def extract text from multiple PDFs
    
    returnsext from multiple PDFs.
    
    Returns a dict mapping filename -> list of pages
    """
    results = {}
    
    for path in pdf_paths:
        pages = extract_text_by_page(path)
        if pages:
            results[path.name] = pages
    
    return results
