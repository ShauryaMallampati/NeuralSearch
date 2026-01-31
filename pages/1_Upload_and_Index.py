"""
Upload & Index Page
handles PDF uploads and building the search index
"""

import streamlit as st
from datetime import datetime

from src.storage import (
    ensure_dirs, save_uploaded_file, list_uploaded_pdfs,
    index_exists, get_index_stats
)
from src.pdf_ingest import extract_from_multiple
from src.chunking import process_all_documents
from src.vector_index import build_index, save_index_and_metadata
from src.ui_bits import page_header, info_box, success_box, warning_box, metric_row

ensure_dirs()

page_header(
    "Upload & Index",
    "Add PDFs and build your searchable knowledge base"
)

# Upload section
st.subheader("1. Upload PDFs")

uploaded_files = st.file_uploader(
    "Drop your PDFs here",
    type=["pdf"],
    accept_multiple_files=True,
    help="You can upload multiple files at once"
)

if uploaded_files:
    saved_count = 0
    for uf in uploaded_files:
        try:
            save_uploaded_file(uf)
            saved_count += 1
        except Exception as e:
            st.error(f"Failed to save {uf.name}: {e}")
    
    if saved_count > 0:
        success_box(f"Saved {saved_count} file(s) to uploads folder!")

# Show current uploads
st.divider()
st.subheader("2. Build Index")

pdfs = list_uploaded_pdfs()

if not pdfs:
    info_box("No PDFs uploaded yet. Upload some documents above to get started!")
else:
    st.write(f"**{len(pdfs)} PDF(s)** ready to index:")
    
    # Show file list in a nice format
    with st.expander("View uploaded files", expanded=False):
        for pdf in pdfs:
            size_kb = pdf.stat().st_size / 1024
            st.text(f"📄 {pdf.name} ({size_kb:.1f} KB)")
    
    # Index building
    if st.button("Build Index", type="primary", use_container_width=True):
        
        progress_bar = st.progress(0, text="Starting...")
        status_text = st.empty()
        
        try:
            # Step 1: Extract text
            status_text.text("Extracting text from PDFs...")
            progress_bar.progress(10, text="Extracting text...")
            
            docs = extract_from_multiple(pdfs)
            
            if not docs:
                warning_box("No text could be extracted from the PDFs. They might be scanned images.")
                st.stop()
            
            # Step 2: Chunk
            status_text.text("Chunking documents...")
            progress_bar.progress(25, text="Chunking...")
            
            chunks = process_all_documents(docs)
            
            if not chunks:
                warning_box("No chunks created. The documents might be empty.")
                st.stop()
            
            # Step 3: Build index (the meaty part)
            status_text.text("Creating embeddings and building index...")
            
            def update_progress(current, total):
                pct = 25 + int((current / total) * 70)
                progress_bar.progress(pct, text=f"Embedding... {current}/{total}")
            
            index, metadata = build_index(chunks, progress_callback=update_progress)
            
            # Step 4: Save
            status_text.text("Saving index...")
            progress_bar.progress(95, text="Saving...")
            
            save_index_and_metadata(index, metadata)
            
            progress_bar.progress(100, text="Done!")
            status_text.empty()
            
            # Store indexing time in session for display
            st.session_state["last_indexed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            success_box("Index built successfully! You can now search your documents.")
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Error building index: {e}")
            st.exception(e)

# Index stats section
st.divider()
st.subheader("3. Index Status")

if index_exists():
    stats = get_index_stats()
    
    if stats:
        last_indexed = st.session_state.get("last_indexed", "Unknown")
        
        metric_row([
            ("Documents", str(stats["total_docs"]), "Number of PDFs indexed"),
            ("Chunks", str(stats["total_chunks"]), "Total searchable passages"),
            ("Embedding Dim", str(stats["embedding_dim"]), "Vector dimensionality"),
            ("Index Size", stats["index_size"], "Size on disk"),
        ])
        
        st.caption(f"Last indexed: {last_indexed}")
        
        with st.expander("Indexed documents"):
            for doc in stats["doc_names"]:
                st.text(f"{doc}")
else:
    info_box(
        "No index built yet. Upload PDFs above and click 'Build Index' to create "
        "your searchable knowledge base."
    )
