"""
NeuralSearch - Semantic PDF search engine
Search your documents by meaning, not keywords
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

import gradio as gr

from src.storage import (
    ensure_dirs,
    list_uploaded_pdfs,
    save_uploaded_path,
    delete_uploaded_file,
    clear_index,
    index_exists,
    get_index_stats,
)
from src.pdf_ingest import extract_from_multiple
from src.chunking import process_all_documents
from src.vector_index import build_index, save_index_and_metadata
from src.search import search as semantic_search, format_citation, highlight_keywords

ensure_dirs()


def _format_docs_list() -> str:
    pdfs = list_uploaded_pdfs()
    if not pdfs:
        return "No documents uploaded yet."
    lines = [f"- {p.name} ({p.stat().st_size / 1024:.1f} KB)" for p in pdfs]
    return "\n".join(lines)


def _format_index_stats() -> str:
    if not index_exists():
        return "No index built yet."
    stats = get_index_stats()
    if not stats:
        return "Index exists but stats are unavailable."
    return (
        f"Documents: {stats['total_docs']}\n"
        f"Chunks: {stats['total_chunks']}\n"
        f"Embedding Dim: {stats['embedding_dim']}\n"
        f"Index Size: {stats['index_size']}"
    )


def upload_and_index(files: list[str] | None, progress=gr.Progress()):
    if not files:
        return "No files uploaded.", _format_docs_list(), _format_index_stats()

    saved = 0
    for file_path in files:
        save_uploaded_path(file_path)
        saved += 1

    progress(0.1, desc="Extracting Text")
    pdfs = list_uploaded_pdfs()
    docs = extract_from_multiple(pdfs)
    if not docs:
        return "No text could be extracted. The PDFs might be scanned images.", _format_docs_list(), _format_index_stats()

    progress(0.3, desc="Chunking")
    chunks = process_all_documents(docs)
    if not chunks:
        return "No chunks created. The documents might be empty.", _format_docs_list(), _format_index_stats()

    progress(0.5, desc="Embedding And Building Index")

    def update_progress(current, total):
        if total:
            progress(0.5 + (current / total) * 0.4, desc=f"Embedding {current}/{total}")

    index, metadata = build_index(chunks, progress_callback=update_progress)

    progress(0.95, desc="Saving")
    save_index_and_metadata(index, metadata)
    progress(1.0, desc="Done")

    msg = f"Index built successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return msg, _format_docs_list(), _format_index_stats()


def rebuild_index(progress=gr.Progress()):
    pdfs = list_uploaded_pdfs()
    if not pdfs:
        return "No PDFs to index.", _format_docs_list(), _format_index_stats()

    progress(0.1, desc="Extracting Text")
    docs = extract_from_multiple(pdfs)
    if not docs:
        return "No text extracted from PDFs.", _format_docs_list(), _format_index_stats()

    progress(0.3, desc="Chunking")
    chunks = process_all_documents(docs)

    progress(0.5, desc="Embedding And Building Index")

    def update_progress(current, total):
        if total:
            progress(0.5 + (current / total) * 0.4, desc=f"Embedding {current}/{total}")

    index, metadata = build_index(chunks, progress_callback=update_progress)

    progress(0.95, desc="Saving")
    save_index_and_metadata(index, metadata)
    progress(1.0, desc="Done")

    return "Index rebuilt successfully.", _format_docs_list(), _format_index_stats()


def clear_index_action():
    clear_index()
    return "Index cleared. Your uploads are untouched.", _format_docs_list(), _format_index_stats()


def delete_selected_uploads(selected: list[str] | None):
    if not selected:
        return "No files selected.", _format_docs_list(), _format_index_stats(), []
    for filename in selected:
        delete_uploaded_file(filename)
    return f"Deleted {len(selected)} file(s).", _format_docs_list(), _format_index_stats(), []


def list_upload_names() -> list[str]:
    return [p.name for p in list_uploaded_pdfs()]


def run_search(query: str, top_k: int, citations: bool, highlight: bool):
    if not index_exists():
        return "No index found. Upload PDFs and build the index first."
    if not query.strip():
        return "Please enter a search query."

    results = semantic_search(query.strip(), k=top_k)
    if not results:
        return "No matching results found. Try rephrasing your query."

    blocks = []
    for i, result in enumerate(results, 1):
        score_pct = int(result["similarity_score"] * 100)
        page_start = result["page_start"]
        page_end = result["page_end"]
        page_str = f"Page {page_start}" if page_start == page_end else f"Pages {page_start}–{page_end}"
        citation = format_citation(result) if citations else result["file_name"]
        text = result["text"]
        display_text = highlight_keywords(text, query) if highlight else text

        blocks.append(
            f"### Result {i}\n"
            f"**{score_pct}% Match**  \n"
            f"{citation}  \n"
            f"{result['file_name']} • {page_str}\n\n"
            f"{display_text}"
        )

    return "\n\n---\n\n".join(blocks)


with gr.Blocks(title="NeuralSearch") as demo:
    gr.Markdown(
        """
        # NeuralSearch
        Semantic PDF search that runs fully offline.

        **How It Works**
        1. Upload PDFs
        2. Build the index (chunking + embeddings)
        3. Search by meaning with citations
        """
    )

    with gr.Tab("Upload And Index"):
        upload_files = gr.Files(label="Upload PDFs", file_types=[".pdf"], type="filepath")
        build_button = gr.Button("Build Index")
        build_status = gr.Textbox(label="Status")
        docs_list = gr.Markdown(value=_format_docs_list())
        stats_box = gr.Textbox(label="Index Stats", value=_format_index_stats())

        build_button.click(
            upload_and_index,
            inputs=[upload_files],
            outputs=[build_status, docs_list, stats_box],
        )

    with gr.Tab("Semantic Search"):
        query = gr.Textbox(label="Search Query", placeholder="What are the main conclusions?")
        top_k = gr.Slider(3, 15, value=5, step=1, label="Top K Results")
        citations = gr.Checkbox(value=True, label="Show Citations")
        highlight = gr.Checkbox(value=True, label="Highlight Keywords")
        search_button = gr.Button("Search")
        search_results = gr.Markdown()

        search_button.click(
            run_search,
            inputs=[query, top_k, citations, highlight],
            outputs=[search_results],
        )

    with gr.Tab("Knowledge Base"):
        kb_docs = gr.Markdown(value=_format_docs_list())
        kb_stats = gr.Textbox(label="Index Stats", value=_format_index_stats())

        rebuild_button = gr.Button("Rebuild Index")
        clear_button = gr.Button("Clear Index")
        delete_group = gr.CheckboxGroup(choices=list_upload_names(), label="Delete Selected Uploads")
        delete_button = gr.Button("Delete Selected Files")
        kb_status = gr.Textbox(label="Status")

        rebuild_button.click(
            rebuild_index,
            inputs=[],
            outputs=[kb_status, kb_docs, kb_stats],
        )

        clear_button.click(
            clear_index_action,
            inputs=[],
            outputs=[kb_status, kb_docs, kb_stats],
        )

        delete_button.click(
            delete_selected_uploads,
            inputs=[delete_group],
            outputs=[kb_status, kb_docs, kb_stats, delete_group],
        )

    gr.Markdown("Built with Gradio, sentence-transformers, and FAISS. Runs fully offline.")


if __name__ == "__main__":
    demo.launch()
