"""
Knowledge Base Page
manage your documents and index
"""

import streamlit as st

from src.storage import (
    ensure_dirs, list_uploaded_pdfs, delete_uploaded_file,
    index_exists, get_index_stats, clear_index
)
from src.pdf_ingest import extract_from_multiple
from src.chunking import process_all_documents
from src.vector_index import build_index, save_index_and_metadata
from src.ui_bits import (
    page_header, info_box, success_box, warning_box, 
    metric_row, empty_state, confirm_action, set_confirm
)

ensure_dirs()

page_header(
    "Knowledge Base",
    "Manage your documents and search index"
)

# Index stats
st.subheader("Index Statistics")

if index_exists():
    stats = get_index_stats()
    
    if stats:
        metric_row([
            ("Total Documents", str(stats["total_docs"]), "PDFs in the index"),
            ("Total Chunks", str(stats["total_chunks"]), "Searchable passages"),
            ("Embedding Dim", str(stats["embedding_dim"]), "Vector size"),
            ("Index Size", stats["index_size"], "Size on disk"),
        ])
        
        with st.expander("Indexed Documents"):
            for doc in sorted(stats["doc_names"]):
                st.text(f"• {doc}")
else:
    info_box("No index exists yet. Upload documents and build an index to get started!")

st.divider()

# Uploaded files management
st.subheader("Uploaded Documents")

pdfs = list_uploaded_pdfs()

if not pdfs:
    empty_state("No documents uploaded yet.")
else:
    st.write(f"**{len(pdfs)}** document(s) in uploads folder:")
    
    # Multi-select for deletion
    selected_for_deletion = []
    
    for pdf in pdfs:
        size_kb = pdf.stat().st_size / 1024
        col1, col2, col3 = st.columns([0.5, 3, 1])
        
        with col1:
            if st.checkbox("", key=f"del_{pdf.name}", label_visibility="collapsed"):
                selected_for_deletion.append(pdf.name)
        
        with col2:
            st.text(f"{pdf.name}")
        
        with col3:
            st.caption(f"{size_kb:.1f} KB")
    
    # Delete selected button
    if selected_for_deletion:
        st.warning(f"{len(selected_for_deletion)} file(s) selected for deletion")
        
        if "confirm_delete_files" not in st.session_state:
            st.session_state.confirm_delete_files = False
        
        if not st.session_state.confirm_delete_files:
            if st.button("Delete Selected Files", type="secondary"):
                st.session_state.confirm_delete_files = True
                st.rerun()
        else:
            st.error("This will permanently delete the selected files!")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Yes, Delete Them", type="primary"):
                    for filename in selected_for_deletion:
                        delete_uploaded_file(filename)
                    st.session_state.confirm_delete_files = False
                    success_box(f"Deleted {len(selected_for_deletion)} file(s). Rebuild the index to update search.")
                    st.rerun()
            
            with col2:
                if st.button("Cancel"):
                    st.session_state.confirm_delete_files = False
                    st.rerun()

st.divider()

# Index management actions
st.subheader("Index Actions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Rebuild Index**")
    st.caption("Re-process all uploaded PDFs and create a fresh index.")
    
    if st.button("Rebuild Index", use_container_width=True, disabled=len(pdfs) == 0):
        if len(pdfs) == 0:
            warning_box("No PDFs to index!")
        else:
            progress = st.progress(0, "Starting rebuild...")
            status = st.empty()
            
            try:
                status.text("Extracting text...")
                progress.progress(10)
                docs = extract_from_multiple(pdfs)
                
                if not docs:
                    warning_box("No text extracted from PDFs.")
                    st.stop()
                
                status.text("Chunking...")
                progress.progress(25)
                chunks = process_all_documents(docs)
                
                status.text("Building embeddings...")
                
                def update_prog(curr, total):
                    pct = 25 + int((curr / total) * 65)
                    progress.progress(pct, f"Embedding {curr}/{total}...")
                
                index, metadata = build_index(chunks, progress_callback=update_prog)
                
                status.text("Saving...")
                progress.progress(95)
                save_index_and_metadata(index, metadata)
                
                progress.progress(100, "Done!")
                status.empty()
                success_box("Index rebuilt successfully!")
                st.rerun()
                
            except Exception as e:
                progress.empty()
                status.empty()
                st.error(f"Rebuild failed: {e}")

with col2:
    st.markdown("**Clear Index**")
    st.caption("Delete the search index. Your uploaded PDFs will be kept.")
    
    if "confirm_clear_index" not in st.session_state:
        st.session_state.confirm_clear_index = False
    
    if not st.session_state.confirm_clear_index:
        if st.button("Clear Index", use_container_width=True, disabled=not index_exists()):
            st.session_state.confirm_clear_index = True
            st.rerun()
    else:
        st.warning("This will delete the search index!")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Clear It"):
                clear_index()
                st.session_state.confirm_clear_index = False
                success_box("Index cleared!")
                st.rerun()
        with c2:
            if st.button("Cancel"):
                st.session_state.confirm_clear_index = False
                st.rerun()

# Help section
st.divider()
with st.expander("Help & Info"):
    st.markdown("""
    ### When to Rebuild the Index
    
    You should rebuild the index when:
    - You've added new PDF documents
    - You've deleted documents and want to remove them from search
    - The index seems corrupted or search isn't working
    
    ### Clearing vs Rebuilding
    
    - **Clear Index**: Only removes the index files. Your PDFs stay in the uploads folder.
    - **Rebuild Index**: Creates a fresh index from all currently uploaded PDFs.
    
    ### Storage
    
    - Uploaded PDFs are stored in `data/uploads/`
    - The search index is stored in `index/`
    """)
