# Indian Legal RAG Assistant

Local retrieval-augmented assistant for the Bharatiya Nyaya Sanhita (BNS),
Bharatiya Nagarik Suraksha Sanhita (BNSS), and Bharatiya Sakshya Adhiniyam
(BSA). It retrieves statute text, reranks evidence, generates through a local
Ollama model, and verifies claims before returning an answer.

## Requirements

- Python 3.11 or 3.12
- Ollama running locally with `llama3.1` available
- Optional CUDA-capable GPU; CPU is selected automatically when CUDA is absent

## Setup

If `.venv` was created with a Python installation that no longer exists, remove
that broken environment before recreating it:

```powershell
Remove-Item -Recurse -Force .venv
```

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
ollama pull llama3.1
```

Place the source PDFs in `data/raw/`, then build the index:

```powershell
python -m src.ingestion.build_knowledge_base
```

Run the web app:

```powershell
streamlit run src/ui/app_streamlit.py
```

## Uploading documents

In the app, open **Add a legal document**, select a text-based PDF, optionally
provide its document or Act label, then select **Index document**. The PDF is
stored locally in `data/uploads/` and its text is added to the Chroma evidence
base. It is searchable immediately after indexing. Scanned PDFs need OCR before
uploading because the app only extracts embedded PDF text.

Each displayed citation opens its local source PDF at the first cited page. The
app copies source PDFs into a Streamlit static directory on demand; those copies
are generated files and are not committed to version control.

## Personal incident support

When a question appears to describe a crime or incident affecting the user, the
app displays a separate **What you can do now** card. This card uses
deterministic, official-channel guidance rather than a generated legal answer:
immediate safety and 112, evidence preservation, reporting steps, cyber-fraud
reporting through 1930 and the National Cyber Crime Reporting Portal, and NALSA
legal-aid information (15100). It does not appear for abstract questions about
criminal-law provisions.

Run tests and the evaluation suite:

```powershell
pytest -q
python -m src.evaluation.evaluate
```

## Safety model

The assistant only answers when retrieved evidence passes the reranker and the
verification step supports every audited claim. Retrieval, generation, or
verification failures result in no answer. It is an informational tool, not a
substitute for professional legal advice.

Set `MODEL_DEVICE=cpu` or `MODEL_DEVICE=cuda` to override automatic hardware
selection.
