"""
Semantic Search Page
the main event - search your documents by meaning
"""

import streamlit as st

from src.storage import ensure_dirs, index_exists
from src.search import search, format_citation, highlight_keywords
from src.ui_bits import page_header, no_index_warning, empty_state

ensure_dirs()

page_header(
    "Semantic Search",
    "Find information by meaning, not just keywords"
)

# Check if index exists
if not index_exists():
    no_index_warning()
    st.stop()

# Search interface
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "What are you looking for?",
        placeholder="e.g., What are the main conclusions about climate change?",
        label_visibility="collapsed"
    )

with col2:
    search_clicked = st.button("Search", type="primary", use_container_width=True)

# Settings in sidebar-ish area
with st.expander("Search Settings", expanded=False):
    col_a, col_b = st.columns(2)
    
    with col_a:
        top_k = st.slider(
            "Number of results",
            min_value=3,
            max_value=15,
            value=5,
            help="How many matching passages to return"
        )
    
    with col_b:
        citations_mode = st.toggle(
            "Citations Mode",
            value=True,
            help="Show formatted citations with page numbers"
        )
        
        highlight_mode = st.toggle(
            "Highlight Keywords",
            value=True,
            help="Highlight query terms in results"
        )

st.divider()

# Perform search
if search_clicked and query.strip():
    with st.spinner("Searching..."):
        results = search(query.strip(), k=top_k)
    
    if results is None:
        no_index_warning()
    elif len(results) == 0:
        empty_state("No matching results found. Try rephrasing your query.")
    else:
        st.subheader(f"Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            score = result["similarity_score"]
            doc_name = result["file_name"]
            page_start = result["page_start"]
            page_end = result["page_end"]
            text = result["text"]
            
            # Format the citation
            if citations_mode:
                citation = format_citation(result)
            else:
                citation = doc_name
            
            # Apply highlighting if enabled
            display_text = highlight_keywords(text, query) if highlight_mode else text
            
            # Score as percentage for friendliness
            score_pct = int(score * 100)
            
            # Page display
            if page_start == page_end:
                page_str = f"Page {page_start}"
            else:
                page_str = f"Pages {page_start}–{page_end}"
            
            # Result card
            with st.container():
                # Header row
                header_col1, header_col2 = st.columns([3, 1])
                
                with header_col1:
                    st.markdown(f"**Result {i}** — {citation}")
                
                with header_col2:
                    # Color code the score
                    if score_pct >= 70:
                        score_color = "HIGH"
                    elif score_pct >= 50:
                        score_color = "MEDIUM"
                    else:
                        score_color = "LOW"
                    st.markdown(f"**{score_pct}%** match ({score_color})")
                
                st.caption(f"{doc_name} • {page_str}")
                
                # Text with expander for full content
                preview_length = 300
                if len(text) > preview_length:
                    st.markdown(display_text[:preview_length] + "...")
                    with st.expander("Show full passage"):
                        st.markdown(display_text)
                else:
                    st.markdown(display_text)
                
                st.divider()

elif search_clicked and not query.strip():
    st.warning("Please enter a search query!")

else:
    # Empty state - show tips
    st.markdown("""
    ### Search Tips
    
    - **Ask natural questions**: "What methods were used to analyze the data?"
    - **Be specific**: "results of experiment 3" works better than just "results"  
    - **Try different phrasings**: Semantic search understands meaning, so synonyms work!
    
    ---
    
    ### Example Queries
    
    - "What are the main conclusions?"
    - "How does the algorithm handle edge cases?"
    - "What are the limitations mentioned?"
    - "Explain the methodology used"
    - "What future work is suggested?"
    """)
