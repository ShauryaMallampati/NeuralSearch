# NeuralSearch

A local semantic search engine for your PDFs. Search by meaning, not keywords.

## What It Does

Upload PDFs, ask questions in plain English, get answers with citations. Like Google, but for your documents — and it actually understands what you're asking.

**100% offline.** No OpenAI, no cloud APIs, no data leaves your machine.

## How It Works

1. **Upload** PDFs to the knowledge base
2. **Chunking** — documents are split into overlapping passages (~300 words each)
3. **Embeddings** — each chunk is converted to a 384-dimensional vector using `all-MiniLM-L6-v2`
4. **Indexing** — vectors are stored in a FAISS index for fast similarity search
5. **Search** — your query is embedded and compared against all chunks using cosine similarity
6. **Results** — top matches are returned with document name and page citations

## Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/VectorVault-NeuralSearch.git
cd VectorVault-NeuralSearch

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Usage

1. Go to **Upload & Index** → drop your PDFs → click "Build Index"
2. Go to **Semantic Search** → ask questions → get results with citations
3. Use **Knowledge Base** to manage documents and rebuild/clear the index

## Example Queries

Try these after indexing some documents:

- "What are the main conclusions?"
- "Explain the methodology used in the study"
- "What limitations are mentioned?"
- "How does the algorithm handle edge cases?"
- "What future work do the authors suggest?"

## Troubleshooting

### FAISS Installation Issues

If `pip install faiss-cpu` fails:

```bash
# Try conda instead
conda install -c conda-forge faiss-cpu

# Or on Mac with Apple Silicon
pip install faiss-cpu --no-cache-dir
```

### "No Index Found" Error

You need to build the index first:
1. Go to Upload & Index page
2. Upload at least one PDF
3. Click "Build Index"

### Search Returns No Results

- Make sure the index was built successfully (check the stats on Upload & Index page)
- Try broader or differently-phrased queries
- Semantic search works best with natural language questions

### Model Download Takes Forever

The embedding model (`all-MiniLM-L6-v2`, ~90MB) downloads on first run. This is a one-time thing. If it's stuck, check your internet connection and try again.

## Tech Stack

- **Streamlit** — UI framework
- **sentence-transformers** — text embeddings (all-MiniLM-L6-v2)
- **FAISS** — vector similarity search
- **pypdf** — PDF text extraction

## Project Structure

```
VectorVault-NeuralSearch/
├── app.py                    # Landing page
├── pages/
│   ├── 1_Upload_and_Index.py # PDF upload + indexing
│   ├── 2_Semantic_Search.py  # Search interface
│   └── 3_Knowledge_Base.py   # Document management
├── src/
│   ├── pdf_ingest.py         # PDF text extraction
│   ├── chunking.py           # Text chunking logic
│   ├── embedder.py           # Embedding model wrapper
│   ├── vector_index.py       # FAISS index management
│   ├── search.py             # Search functionality
│   ├── storage.py            # File I/O utilities
│   └── ui_bits.py            # Reusable UI components
├── data/uploads/             # Uploaded PDFs (gitignored)
├── index/                    # FAISS index + metadata (gitignored)
├── requirements.txt
└── README.md
```

## License

MIT — do whatever you want with it.
