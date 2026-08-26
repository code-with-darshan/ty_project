# Indian Legal RAG Assistant

A fully local, hallucination-aware Retrieval-Augmented Generation (RAG) system for Indian law.
Query across 40+ Indian statutes — criminal, civil, family, labour, corporate, IP, consumer,
environmental, tax, and constitutional law — with every answer grounded in statute text and
verified before it reaches you.

---

## Tech Stack

| Layer                   | Technology                                               | Purpose                                                        |
|-------------------------|----------------------------------------------------------|----------------------------------------------------------------|
| **LLM (local)**         | Llama 3.1 8B via [Ollama](https://ollama.com/)           | Query expansion, answer generation, and claim verification     |
| **LLM API adapter**     | `openai` Python SDK (v1)                                 | OpenAI-compatible interface to Ollama's local endpoint         |
| **Embeddings**          | `BAAI/bge-small-en-v1.5` (sentence-transformers)         | Dense vector representations of statute chunks and queries     |
| **Vector store**        | [ChromaDB](https://www.trychroma.com/) (persistent)      | Stores and retrieves dense embeddings for semantic search      |
| **Sparse retrieval**    | BM25 (`rank-bm25`)                                       | Keyword-based retrieval fused with dense search via RRF        |
| **Reranker**            | `cross-encoder/ms-marco-MiniLM-L-6-v2`                   | Cross-encoder scoring to reorder evidence by relevance         |
| **PDF ingestion**       | PyMuPDF (`fitz`)                                         | Extracts embedded text from legal PDF documents                |
| **Web UI**              | [Streamlit](https://streamlit.io/)                       | Conversational query interface with citations and upload panel |
| **Evaluation**          | pandas · scikit-learn · matplotlib                       | Batch evaluation, metrics reporting, and chart generation      |
| **Hardware selection**  | PyTorch (`torch`)                                        | Auto-detects CUDA; falls back to CPU                           |
| **Testing**             | pytest                                                   | Unit and integration test suite                                |
| **Language**            | Python 3.11 / 3.12                                       | Primary implementation language                                |

---

## Architecture — 6-Stage RAG Pipeline

```
User Query
    │
    ▼
[1] QueryExpander          – Few-shot LLM prompt translates colloquial language
    │                        into precise statutory terminology
    ▼
[2] VectorSearcher         – Hybrid search: dense embeddings (ChromaDB) +
    │                        sparse BM25, fused via Reciprocal Rank Fusion (RRF)
    ▼
[3] Reranker               – Cross-encoder (ms-marco-MiniLM-L-6-v2) rescores
    │                        and reorders evidence for relevance to the original query
    ▼
[4] LegalGenerator         – Evidence-First protocol: only chunks above the
    │                        relevance threshold are used; answer refused if none pass
    ▼
[5] AnswerVerifier         – Chain-of-Verification: each claim is audited against
    │                        the retrieved evidence; composite confidence scored
    ▼
Final Response             – Verified answer with citations, confidence tier,
                             and optional incident guidance card
```

---

## Key Components

### Retrieval (`src/retrieval/`)
| File                  | Role                                                                                                      |
|-----------------------|-----------------------------------------------------------------------------------------------------------|
| `query_expander.py`   | Translates slang/informal queries to formal statutory terms using  few-shot Ollama prompting              |
|                       |                                                                                                           |
| `vector_search.py`    | Hybrid search: dense vectors (ChromaDB) + BM25, combined via Reciprocal Rank Fusion (RRF, k=60)           |
|                       |                                                                                                           |
| `reranker.py`         | Cross-encoder reranking using|`cross-encoder/besfems-marco-MiniLM-L-6-v2`                                 |

### Generation (`src/generation/`)
| File            | Role                                                                                                                |
| `generator.py`  | Filters chunks below relevance threshold, assembles evidence context, generates answer via Llama 3.1 through Ollama |

### Verification (`src/verification/`)
| File           | Role     
| `verifier.py`  | **3-Layer refusal system**: (1) insufficient evidence, (2) composite score < 40%, (3) any unsupported claim → hallucination refusal. Outputs confidence tier: *High Confidence* (≥ 80%) or *Moderate Confidence* (40–79%). |

### Safety (`src/safety/`)
| File                    | Role 
| `incident_response.py`  | Deterministic, pattern-matched incident guidance card for personal crime reports. Covers general crime, cyber/financial fraud, and immediate-danger scenarios. Links to 112, 1930, cybercrime.gov.in, and NALSA. |

### Ingestion (`src/ingestion/`)
| File                       | Role                                                                                                                                  |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `build_knowledge_base.py`  | Loads PDFs from `data/raw/`, cleans and chunks them, generates embeddings via `BAAI/bge-small-en-v1.5`, and upserts into ChromaDB.    |
|                            | Recognises 40+ act names automatically.                                                                                               |
| `chunker.py`               | Section-aware chunker with 1000-token chunks and 200-token  overlap                                                                   |
| `pdf_loader.py`            | Embedded text extraction via PyMuPDF (scanned PDFs need OCR pre-processing)                                                           |
| `text_cleaner.py`          | Statutory text normalisation                                                                                                          |

### Embeddings (`src/embeddings/`)
| File           | Role                                                                                   |
|----------------|----------------------------------------------------------------------------------------|
| `embedder.py`  | Wraps `sentence-transformers` with `BAAI/bge-small-en-v1.5`; auto-selects CUDA or CPU  | 

### UI (`src/ui/`)
```markdown
| File                 | Role                                                                                                                  |
-----------------------------------------------------------------------------------------------------------------------------------------------|
| `app_streamlit.py`   | Full Streamlit web app with query interface, citation links (opens source PDF at cited page), document upload panel,and incident guidance card rendering   |
|                      |                                                                                   |
| `document_links.py`  | Resolves local PDF paths and copies them into Streamlit's static directory on demand
                                                                  


### Evaluation (`src/evaluation/`)
| File          | Role                                                                                                                  |
|---------------|-----------------------------------------------------------------------------------------------------------------------|
| `evaluate.py` | Batch evaluation pipeline: runs a labelled test set through the full pipeline, measures safety-guardrail accuracy with| 
|               | scikit-learn, and saves `evaluation_results.csv` + `performance_dashboard.png`                                        |


## Supported Legal Domains

| Domain                        |                ExampleActs                                                                                                           |
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Criminal**                  | BNS, BNSS, BSA (IPC / CrPC / Indian Evidence Act legacy docs also supported)                                                         |
| **Civil / Contract**          | Indian Contract Act 1872, Specific Relief Act 1963, Limitation Act 1963, Arbitration and Conciliation Act 1996                       |
| **Property**                  | Transfer of Property Act 1882, Registration Act 1908                                                                                 |
| **Family / Personal**         | Hindu Marriage Act 1955, Hindu Succession Act 1956, Dowry Prohibition Act 1961, Protection of Women from Domestic Violence Act 2005  |
| **Consumer / RTI / Digital**  | Consumer Protection Act 2019, RTI Act 2005, IT Act 2000                                                                              |
| **Labour**                    | Factories Act 1948, Industrial Disputes Act 1947, Minimum Wages Act 1948, Maternity Benefit Act 1961                                 |
| **Corporate / Insolvency**    | Companies Act 2013, IBC 2016, LLP Act 2008                                                                                           |
| **Intellectual Property**     | Copyright Act 1957, Trade Marks Act 1999, Patents Act 1970                                                                           |
| **Environment**               | Environment Protection Act 1986, Wildlife Protection Act 1972                                                                        |
| **Tax**                       | Income Tax Act 1961, GST Act 2017                                                                                                    |
| **Constitutional**            | Constitution of India                                                                                                                |

## Requirements

- Python 3.11 or 3.12
- [Ollama](https://ollama.com/) running locally with `llama3.1` available
- Optional CUDA-capable GPU; CPU is selected automatically when CUDA is absent

---

## Setup

If an existing `.venv` was created with a Python installation that no longer exists, remove it first:

```powershell
Remove-Item -Recurse -Force .venv
```

Create and activate a fresh environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
ollama pull llama3.1
```

---

## Building the Knowledge Base

Place your legal PDFs in `data/raw/` — the ingestion pipeline auto-detects the Act from the filename:

```powershell
python -m src.ingestion.build_knowledge_base
```

> **Scanned PDFs**: The loader extracts embedded PDF text only. Run OCR on scanned documents before ingestion.

---

## Running the Web App

```powershell
streamlit run src/ui/app_streamlit.py
```

### Upload a Document at Runtime

In the app sidebar, open **Add a legal document**, select a text-based PDF, optionally provide a document or Act label, then click **Index document**. The PDF is stored in `data/uploads/` and immediately searchable.

### Citations

Each citation in the answer links to the source PDF, opened at the first cited page. Source PDFs are copied into Streamlit's static directory on demand; those copies are generated files and are not committed to version control.

---

## Incident Guidance

When a query appears to describe a personal crime or incident (pattern-matched, not LLM-driven), the app shows a **"What you can do now"** card with:

- **Immediate danger** — call 112
- **Cyber / financial fraud** — call 1930, report at [cybercrime.gov.in](https://cybercrime.gov.in/)
- **General incidents** — evidence preservation steps, police reporting guidance
- **Legal aid** — NALSA helpline 15100 ([nalsa.gov.in](https://nalsa.gov.in/))

This card uses deterministic, official-channel guidance and does **not** appear for abstract law questions.

---

## Evaluation

```powershell
pytest -q
python -m src.evaluation.evaluate
```

The evaluation script runs a labelled test set through the full pipeline and produces:

| Output                       | Description                                                             |
|------------------------------|-------------------------------------------------------------------------|
| `evaluation_results.csv`     | Per-query results: expected vs actual action, confidence score, latency |
| `performance_dashboard.png`  | Confidence score distribution + latency chart                           |

Metrics reported: safety-guardrail accuracy, precision, recall, and F1 via scikit-learn.

---

## Configuration

All tuneable parameters live in `config/settings.py`:

| Parameter               | Default                                  | Description                                                         |
|-------------------------|------------------------------------------|---------------------------------------------------------------------|
| `EMBEDDING_MODEL`       | `BAAI/bge-small-en-v1.5`                 | Sentence-transformer model for dense retrieval                      |
| `RERANKER_MODEL`        | `cross-encoder/ms-marco-MiniLM-L-6-v2`   | Cross-encoder for evidence reranking                                |
| `INITIAL_RETRIEVAL_K`   | `25`                                     | Candidates fetched from ChromaDB + BM25 before reranking            |
| `RERANK_TOP_K`          | `4`                                      | Evidence chunks kept after reranking                                |
| `RELEVANCE_THRESHOLD`   | `-3.0`                                   | Minimum cross-encoder score to pass to generation                   |
| `CHUNK_SIZE`            | `1000`                                   | Token budget per chunk                                              |
| `CHUNK_OVERLAP`         | `200`                                    | Token overlap between consecutive chunks                            |
| `OLLAMA_MODEL`          | `llama3.1`                               | Local Ollama model for query expansion, generation, and verification|
| `MODEL_DEVICE`          | auto-detected                            | Override with `MODEL_DEVICE=cpu` or `MODEL_DEVICE=cuda`             |



## Safety Model

The assistant enforces a multi-layer refusal policy:

1. **No evidence** — no chunks pass the relevance threshold → refuses to answer
2. **Low composite confidence** (< 40%) — verification ratio + retrieval quality too low → refuses
3. **Unsupported claim** — any claim in the answer is not grounded in evidence → hallucination refusal

Only answers where all claims are supported and composite confidence ≥ 40% are returned. This is an informational tool; consult a qualified lawyer for legal advice.

---

## Project Structure

```
Legal-rag-assistant/
├── app.py                        # LegalRAGPipeline — wires all 6 stages
├── config/
│   └── settings.py               # All tuneable constants
├── data/
│   ├── raw/                      # Source legal PDFs (not committed)
│   ├── uploads/                  # User-uploaded PDFs
│   └── chroma_db/                # Persistent ChromaDB vector store
├── src/
│   ├── ingestion/                # PDF loading, cleaning, chunking, indexing
│   ├── embeddings/               # BAAI/bge-small-en-v1.5 wrapper
│   ├── retrieval/                # Query expansion, hybrid search (RRF), reranker
│   ├── generation/               # Evidence-first LLM generation
│   ├── verification/             # Chain-of-Verification + confidence scoring
│   ├── safety/                   # Deterministic incident guidance
│   └── ui/                       # Streamlit web app + PDF link resolver
├── tests/                        # pytest test suite
├── src/evaluation/evaluate.py    # Batch evaluation + metrics + charts
├── requirements.txt
└── README.md
```
