"""
NeuralSearch - semantic PDF search engine
search your docs by meaning instead of keywords
"""

import streamlit as st
from src.storage import ensure_dirs

# setup directories at startup
ensure_dirs()

# Page config
st.set_page_config(
    page_title="NeuralSearch",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main landing page
st.title("NeuralSearch")
st.subheader("Neural Search for Your PDFs")

st.markdown("""
---

### What is this?

**NeuralSearch** is like Google, but for your PDF documents. Instead of searching 
for exact keywords, it understands the *meaning* behind your queries and finds 
the most relevant passages.

Upload a bunch of research papers, manuals, or any PDFs — then ask questions in 
plain English. NeuralSearch will show you exactly where to find the answers, 
complete with citations.

---

### How it works

1. **Upload** your PDF documents
2. **Index** — we chunk the text and create "meaning vectors" (embeddings)
3. **Search** — ask anything, get relevant results with page citations

All processing happens **locally on your machine**. No cloud APIs, no data leaving 
your computer.

---

### Get Started

Use the sidebar to navigate:

| Page | What it does |
|------|-------------|
| **Upload & Index** | Add PDFs and build the search index |
| **Semantic Search** | Search your documents by meaning |
| **Knowledge Base** | Manage your documents and index |

---

### Quick Notes

- **First time?** Head to "Upload & Index" first
- **Search tips:** Ask natural questions like "What are the main findings about X?"
- **Citations:** Results show exactly which document and page(s) the info came from
- **100% offline:** Everything runs locally after initial setup

""")

# Footer
st.markdown("---")
st.caption("Built with Streamlit, sentence-transformers, and FAISS • Runs entirely offline")

# Footer
st.markdown("---")
st.caption("Built with Streamlit, sentence-transformers, and FAISS • Runs entirely offline")
