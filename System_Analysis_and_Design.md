# System Analysis and Design
## Nyaya — Indian Legal RAG Assistant

---

## 1. Detailed Life Cycle of the Project

The Nyaya project follows an **Iterative RAG-Augmented SDLC** model, combining Agile sprints with the unique requirements of an AI/ML pipeline.

### Phase 1 — Requirements & Research
- Identify the problem: No accessible, statute-grounded legal Q&A system for Indian law.
- Research existing RAG pipelines, LLM hallucination mitigation strategies, and Indian legal corpora.
- Define functional requirements (multi-domain legal Q&A, citation grounding, hallucination detection) and non-functional requirements (local execution, privacy, no external API calls except embeddings).

### Phase 2 — System Design
- Design the multi-stage pipeline: Query Expansion → Hybrid Search → Re-ranking → Generation → Verification.
- Design the knowledge base schema (ChromaDB collections with structured metadata).
- Select technology stack: Python, LangChain-free custom pipeline, ChromaDB, Sentence-Transformers, Ollama (Llama 3.1), Streamlit.

### Phase 3 — Data Ingestion & Knowledge Base Construction
- Collect Indian legal PDFs (BNS, CrPC/BNSS, IPC, Consumer Protection Act, Hindu Marriage Act, IT Act 2000, RTI Act, etc.).
- Build the ingestion pipeline: `pdf_loader.py` → `text_cleaner.py` → `chunker.py` → `metadata.py` → `build_knowledge_base.py`.
- Chunk text at 512 tokens with 64-token overlap; tag each chunk with `act`, `section`, `pages` metadata.
- Generate embeddings using `all-MiniLM-L6-v2` and store in ChromaDB's persistent vector store.

### Phase 4 — Core Pipeline Development
- Implement `QueryExpander` (few-shot LLM-based slang-to-statute translation).
- Implement `VectorSearcher` (Hybrid: Dense ChromaDB + Sparse BM25 fused via Reciprocal Rank Fusion).
- Implement `Reranker` (MS-MARCO cross-encoder for precise relevance scoring).
- Implement `LegalGenerator` (Evidence-First generation with mandatory citation protocol via Ollama).
- Implement `AnswerVerifier` (Chain-of-Verification with composite confidence scoring).

### Phase 5 — User Interface Development
- Build Streamlit frontend (`app_streamlit.py`) with Indian legal theme (Tiranga motif, dark navy/saffron palette).
- Implement PDF upload/indexing form, chat interface, incident guides, and citation drawer.

### Phase 6 — Testing & Evaluation
- Unit tests for all pipeline components (`tests/` directory).
- End-to-end evaluation: generate `evaluation_results.csv` with precision/recall metrics.
- Generate `performance_dashboard.png` for visual performance overview.

### Phase 7 — Safety Module & Hardening
- Implement `incident_response.py` for real-world emergency situations (suicide, domestic abuse, etc.).
- Add input validation, upload size limits (25 MB), and graceful degradation when Ollama is unavailable.

### Phase 8 — Documentation & Deployment
- Write `README.md`, generate `Project_Report_Stage1.docx` (Chapters 1–4).
- Package as a locally deployable application with clear dependency management via `requirements.txt`.

### Life Cycle Summary Diagram

```mermaid
gantt
    title Nyaya Project Life Cycle
    dateFormat  YYYY-MM
    section Research
    Requirements & Research        :done, r1, 2024-08, 2024-09
    section Design
    System & DB Design             :done, d1, 2024-09, 2024-10
    section Build
    Data Ingestion Pipeline        :done, b1, 2024-10, 2024-11
    Core RAG Pipeline              :done, b2, 2024-11, 2025-01
    UI Development                 :done, b3, 2025-01, 2025-02
    section Validate
    Testing & Evaluation           :done, v1, 2025-02, 2025-03
    Safety & Hardening             :done, v2, 2025-03, 2025-04
    section Deploy
    Documentation & Deployment     :active, dep1, 2025-04, 2025-08
```

---

## 2. Context Diagram

The Context Diagram shows the system boundary of **Nyaya** and how it interacts with external entities.

```mermaid
graph TD
    User(["👤 End User\n(Citizen / Law Student\n/ Practitioner"])
    Admin(["🛠️ Administrator\n(Knowledge Base Manager)"])
    LegalDocs(["📚 Legal PDF Corpus\n(Indian Statutes &\nActs)"])
    Ollama(["🤖 Ollama LLM Server\n(Llama 3.1 — Local)"])
    ChromaDB(["🗄️ ChromaDB\n(Persistent Vector Store)"])
    Nyaya["⚖️ NYAYA\nIndian Legal RAG\nAssistant System"]

    User -- "Natural Language Query" --> Nyaya
    Nyaya -- "Legal Answer + Citations\n+ Confidence Score" --> User
    Admin -- "Upload Legal PDFs" --> Nyaya
    LegalDocs -- "Ingest & Index" --> Nyaya
    Nyaya -- "LLM Prompts\n(Query Expand, Generate,\nVerify)" --> Ollama
    Ollama -- "Generated Text\nJSON Audit Results" --> Nyaya
    Nyaya -- "Store / Retrieve\nEmbeddings & Metadata" --> ChromaDB
    ChromaDB -- "Retrieved Evidence Chunks" --> Nyaya
```

---

## 3. DFD, ERD, Class Diagram, State Transition Diagram

### 3.1 Data Flow Diagram (DFD)

#### Level 0 — Context DFD

```mermaid
graph LR
    U(["User"]) -- Query --> S["Nyaya System"]
    S -- Answer + Citations --> U
    A(["Admin"]) -- PDF Upload --> S
    S -- Indexed Chunks --> DB[(ChromaDB)]
```

#### Level 1 — Main DFD

```mermaid
graph TD
    U(["User"]) -- "Query" --> P1["1.0\nQuery Expansion"]
    P1 -- "Expanded Query" --> P2["2.0\nHybrid Search\n(Dense + BM25)"]
    P2 -- "Raw Chunks" --> P3["3.0\nCross-Encoder\nRe-ranking"]
    P3 -- "Ranked Chunks" --> P4["4.0\nEvidence-First\nGeneration"]
    P4 -- "Draft Answer" --> P5["5.0\nChain-of-Verification\n& Confidence Scoring"]
    P5 -- "Verified Answer" --> U

    DB[(ChromaDB\nVector Store)] -- "Top-K Vectors" --> P2
    BM[(BM25 Index\nin Memory)] -- "Top-K Sparse Hits" --> P2
    LLM[(Ollama\nLlama 3.1)] -- "Expanded Terms" --> P1
    LLM -- "Generated Answer" --> P4
    LLM -- "Claims Audit JSON" --> P5
    KB[(Legal PDF\nCorpus)] -- "Raw PDF Text" --> INGEST["0.0\nIngestion Pipeline"]
    INGEST -- "Embeddings + Metadata" --> DB
    INGEST -- "Tokenized Docs" --> BM
```

#### Level 2 — Ingestion Sub-process DFD

```mermaid
graph LR
    PDF(["Legal PDF"]) --> L["2.1\nPDF Loader\npdf_loader.py"]
    L -- "Raw Text Pages" --> C["2.2\nText Cleaner\ntext_cleaner.py"]
    C -- "Cleaned Text" --> CH["2.3\nChunker\nchunker.py"]
    CH -- "512-Token Chunks" --> M["2.4\nMetadata Tagger\nmetadata.py"]
    M -- "Tagged Chunks" --> E["2.5\nEmbedder\nembedder.py"]
    E -- "Vector + Metadata" --> KB["2.6\nKnowledge Base Builder\nbuild_knowledge_base.py"]
    KB -- "Upsert" --> DB[(ChromaDB)]
```

---

### 3.2 Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    LEGAL_DOCUMENT {
        string doc_id PK
        string source_name
        string act_name
        string file_path
        datetime ingested_at
    }

    CHUNK {
        string chunk_id PK
        string doc_id FK
        string text
        int    start_char
        int    end_char
        string act
        string section
        string pages
    }

    EMBEDDING {
        string chunk_id PK_FK
        float[] vector_384d
        string model_name
    }

    QUERY_SESSION {
        string session_id PK
        string user_query
        string expanded_query
        datetime queried_at
    }

    RETRIEVAL_RESULT {
        string result_id PK
        string session_id FK
        string chunk_id FK
        float  rrf_score
        float  rerank_score
    }

    ANSWER {
        string answer_id PK
        string session_id FK
        string generated_text
        string verified_text
        float  confidence_score
        string confidence_tier
        bool   unsupported_flag
    }

    LEGAL_DOCUMENT ||--o{ CHUNK : "contains"
    CHUNK ||--|| EMBEDDING : "has"
    QUERY_SESSION ||--o{ RETRIEVAL_RESULT : "produces"
    RETRIEVAL_RESULT }o--|| CHUNK : "references"
    QUERY_SESSION ||--|| ANSWER : "generates"
```

---

### 3.3 Class Diagram

```mermaid
classDiagram
    class LegalRAGPipeline {
        +QueryExpander expander
        +VectorSearcher searcher
        +Reranker reranker
        +LegalGenerator generator
        +AnswerVerifier verifier
        +query(user_query: str) dict
    }

    class QueryExpander {
        -str model_name
        -OpenAI client
        +expand_query(query: str) str
    }

    class VectorSearcher {
        -Embedder embedder
        -chromadb.Collection collection
        -BM25Okapi bm25
        -list all_documents
        -list all_metadatas
        +search(query: str, top_k: int) list[dict]
    }

    class Embedder {
        -SentenceTransformer model
        +encode_query(query: str) ndarray
        +encode_batch(texts: list) ndarray
    }

    class Reranker {
        -CrossEncoder model
        +rerank(query: str, chunks: list[dict]) list[dict]
    }

    class LegalGenerator {
        -str model_name
        -OpenAI client
        -_filter_chunks(ranked_results: list) list
        -_assemble_context(valid_chunks: list) str
        +generate_answer(query: str, ranked_results: list) dict
    }

    class AnswerVerifier {
        -str model_name
        -OpenAI client
        +verify_and_score(query: str, answer: str, chunks: list) dict
    }

    class KnowledgeBaseBuilder {
        +index_uploaded_pdf(path, source_name, act_name) int
        +build_from_directory(pdf_dir: Path) None
    }

    class PDFLoader {
        +load(path: Path) list[str]
    }

    class TextCleaner {
        +clean(text: str) str
    }

    class Chunker {
        +chunk(text: str, size: int, overlap: int) list[str]
    }

    LegalRAGPipeline --> QueryExpander
    LegalRAGPipeline --> VectorSearcher
    LegalRAGPipeline --> Reranker
    LegalRAGPipeline --> LegalGenerator
    LegalRAGPipeline --> AnswerVerifier
    VectorSearcher --> Embedder
    KnowledgeBaseBuilder --> PDFLoader
    KnowledgeBaseBuilder --> TextCleaner
    KnowledgeBaseBuilder --> Chunker
    KnowledgeBaseBuilder --> Embedder
```

---

### 3.4 State Transition Diagram

Shows the lifecycle of a user query through the Nyaya pipeline.

```mermaid
stateDiagram-v2
    [*] --> Idle : System Ready

    Idle --> QueryReceived : User submits query

    QueryReceived --> CheckingEmergency : Safety module triggered

    CheckingEmergency --> IncidentGuideShown : Emergency detected
    CheckingEmergency --> QueryExpanding : No emergency

    IncidentGuideShown --> QueryExpanding : Continue with query

    QueryExpanding --> HybridSearching : Expanded query ready
    QueryExpanding --> QueryExpanding : LLM expansion failed (fallback to original)

    HybridSearching --> Reranking : Raw chunks retrieved
    HybridSearching --> NoEvidenceFound : Empty result set

    Reranking --> EvidenceFiltering : Rerank scores computed
    
    EvidenceFiltering --> NoEvidenceFound : All chunks below threshold
    EvidenceFiltering --> Generating : Valid chunks available

    Generating --> Verifying : Draft answer produced
    Generating --> ServiceUnavailable : Ollama connection failed

    Verifying --> HighConfidence : Score ≥ 80%
    Verifying --> ModerateConfidence : 40% ≤ Score < 80%
    Verifying --> HallucinationRefused : Unsupported claim detected
    Verifying --> InsufficientEvidence : Score < 40%
    Verifying --> VerificationFailed : Verifier service unavailable

    HighConfidence --> AnswerReturned : Verified answer shown to user
    ModerateConfidence --> AnswerReturned

    NoEvidenceFound --> AnswerReturned : Refusal message shown
    HallucinationRefused --> AnswerReturned : Refusal message shown
    InsufficientEvidence --> AnswerReturned : Refusal message shown
    ServiceUnavailable --> AnswerReturned : Error message shown
    VerificationFailed --> AnswerReturned : Error message shown

    AnswerReturned --> Idle : Ready for next query
```

---

## 4. Use Case Diagram

```mermaid
graph TB
    User(["👤 General User"])
    LawStudent(["📖 Law Student"])
    Admin(["🛠️ Admin"])

    subgraph Nyaya System
        UC1["Ask Legal Question"]
        UC2["View Answer with Citations"]
        UC3["View Confidence Score"]
        UC4["View Incident Guide"]
        UC5["Upload Legal PDF"]
        UC6["Index New Document"]
        UC7["Browse Chat History"]
        UC8["Query Expansion ❰extend❱"]
        UC9["Hybrid Search ❰extend❱"]
        UC10["Re-ranking ❰extend❱"]
        UC11["Verification & Scoring ❰extend❱"]
    end

    User --> UC1
    User --> UC4
    User --> UC7
    LawStudent --> UC1
    LawStudent --> UC2
    LawStudent --> UC3
    LawStudent --> UC5
    Admin --> UC5
    Admin --> UC6

    UC1 -.->|include| UC8
    UC8 -.->|include| UC9
    UC9 -.->|include| UC10
    UC10 -.->|include| UC11
    UC11 -.->|include| UC2
    UC11 -.->|include| UC3
```

### Use Case Descriptions

| Use Case | Actor | Description |
|---|---|---|
| Ask Legal Question | User, Law Student | Submit a natural language query about any domain of Indian law |
| View Answer with Citations | User, Law Student | Read the statute-grounded answer with PDF evidence citations |
| View Confidence Score | Law Student | Inspect the composite verification confidence badge (High/Moderate) |
| View Incident Guide | User | Access deterministic emergency response steps for crisis situations |
| Upload Legal PDF | Law Student, Admin | Upload a new Indian statute PDF for indexing |
| Index New Document | Admin | Trigger chunking, embedding, and ChromaDB ingestion of uploaded PDF |
| Browse Chat History | User | Review previous Q&A exchanges in the session |
| Query Expansion | System | Translate colloquial terms to formal statutory language via LLM |
| Hybrid Search | System | Retrieve evidence via Dense Vector + BM25 with RRF fusion |
| Re-ranking | System | Score retrieved chunks using MS-MARCO cross-encoder |
| Verification & Scoring | System | Audit draft answer claims and compute composite confidence score |

---

## 5. Activity, Component, and Collaboration Diagrams

### 5.1 Activity Diagram — Query Answering Workflow

```mermaid
flowchart TD
    Start([▶ Start]) --> A[Receive User Query]
    A --> B{Emergency\nKeywords?}
    B -- Yes --> C[Load Incident Guide\nincident_response.py]
    C --> D[Display Incident Guide\nto User]
    D --> E[Expand Query via LLM\nQueryExpander]
    B -- No --> E
    E --> F{Expansion\nSucceeded?}
    F -- No --> G[Use Original Query as-is]
    F -- Yes --> H[Use Expanded Query]
    G --> I
    H --> I[Dense Vector Search\nChromaDB query_embeddings]
    I --> J[BM25 Keyword Search\nBM25Okapi scores]
    J --> K[Reciprocal Rank Fusion\nRRF merge I + J]
    K --> L[Cross-Encoder Re-ranking\nReranker.rerank]
    L --> M[Relevance Threshold Filter\nscore ≥ RELEVANCE_THRESHOLD]
    M --> N{Valid\nChunks?}
    N -- No --> O[Return Evidence-Refusal Response]
    N -- Yes --> P[Assemble Evidence Context\nassemble_context]
    P --> Q[Generate Answer via Ollama\nLegalGenerator.generate_answer]
    Q --> R{Generation\nSucceeded?}
    R -- No --> S[Return Service-Unavailable Message]
    R -- Yes --> T[Chain-of-Verification Audit\nAnswerVerifier.verify_and_score]
    T --> U[Compute Composite\nConfidence Score]
    U --> V{Score < 40%?}
    V -- Yes --> W[Return Insufficient Evidence Refusal]
    V -- No --> X{Unsupported\nClaims?}
    X -- Yes --> Y[Return Hallucination-Detected Refusal]
    X -- No --> Z[(Return Verified Answer\n+ Citations + Confidence Badge)]
    W --> End([■ End])
    Y --> End
    Z --> End
    O --> End
    S --> End
```

---

### 5.2 Component Diagram

```mermaid
graph TB
    subgraph UI Layer
        UI["app_streamlit.py\nStreamlit Frontend"]
        DOC_LINKS["document_links.py\nCitation URL Generator"]
    end

    subgraph Application Layer
        PIPELINE["app.py\nLegalRAGPipeline\nOrchestrator"]
        SAFETY["incident_response.py\nEmergency Guide Engine"]
    end

    subgraph Pipeline Components
        QE["query_expander.py\nQueryExpander"]
        VS["vector_search.py\nVectorSearcher\nHybrid Search + RRF"]
        RR["reranker.py\nReranker\nCross-Encoder"]
        GEN["generator.py\nLegalGenerator\nEvidence-First Gen"]
        VER["verifier.py\nAnswerVerifier\nCoV + Confidence"]
    end

    subgraph Ingestion Layer
        BUILD["build_knowledge_base.py\nKB Builder"]
        PDF["pdf_loader.py"]
        CLEAN["text_cleaner.py"]
        CHUNK["chunker.py"]
        META["metadata.py"]
    end

    subgraph Embedding
        EMB["embedder.py\nEmbedder\nall-MiniLM-L6-v2"]
    end

    subgraph External Services
        OLLAMA["🤖 Ollama\nLlama 3.1\nLocal LLM Server"]
        CHROMA["🗄️ ChromaDB\nPersistent Vector Store"]
        MSMARCO["📊 MS-MARCO\nCross-Encoder Model"]
        MINILM["🔡 Sentence-Transformers\nall-MiniLM-L6-v2"]
    end

    UI --> PIPELINE
    UI --> DOC_LINKS
    UI --> SAFETY
    UI --> BUILD

    PIPELINE --> QE
    PIPELINE --> VS
    PIPELINE --> RR
    PIPELINE --> GEN
    PIPELINE --> VER
    PIPELINE --> SAFETY

    QE --> OLLAMA
    GEN --> OLLAMA
    VER --> OLLAMA

    VS --> EMB
    VS --> CHROMA
    RR --> MSMARCO
    EMB --> MINILM

    BUILD --> PDF
    BUILD --> CLEAN
    BUILD --> CHUNK
    BUILD --> META
    BUILD --> EMB
    BUILD --> CHROMA
```

---

### 5.3 Collaboration Diagram (Object Interaction)

The following sequence shows the collaboration between objects during a single query:

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant P as LegalRAGPipeline
    participant QE as QueryExpander
    participant VS as VectorSearcher
    participant RR as Reranker
    participant GEN as LegalGenerator
    participant VER as AnswerVerifier
    participant OLLAMA as Ollama LLM
    participant DB as ChromaDB

    U->>UI: submit("What is murder punishment?")
    UI->>P: query(user_query)
    P->>QE: expand_query(user_query)
    QE->>OLLAMA: chat.completions(few-shot prompt)
    OLLAMA-->>QE: "culpable homicide amounting to murder BNS Section 103"
    QE-->>P: expanded_query

    P->>VS: search(expanded_query)
    VS->>DB: query_embeddings([...])
    DB-->>VS: top-K vector results
    VS->>VS: bm25.get_scores(tokens)
    VS->>VS: RRF_fusion(vector, bm25)
    VS-->>P: ranked_chunks[20]

    P->>RR: rerank(user_query, chunks)
    RR->>RR: cross_encoder.predict(pairs)
    RR-->>P: ranked_chunks[20] with rerank_scores

    P->>GEN: generate_answer(query, ranked_chunks)
    GEN->>GEN: filter_chunks(threshold)
    GEN->>OLLAMA: chat.completions(evidence-first prompt)
    OLLAMA-->>GEN: draft_answer + citations
    GEN-->>P: {answer, citations, valid_chunks}

    P->>VER: verify_and_score(query, answer, chunks)
    VER->>OLLAMA: chat.completions(verification prompt)
    OLLAMA-->>VER: {"claims": [{...}]}
    VER->>VER: compute_confidence_score()
    VER-->>P: {verified_answer, confidence_score, tier}

    P-->>UI: {answer, citations, confidence_score, tier}
    UI-->>U: Display answer + badge + citation drawer
```

---

## 6. Architecture Design

### 6.1 High-Level Architecture

Nyaya follows a **Layered Modular Architecture** with a strict separation between ingestion, retrieval, generation, and verification layers.

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI["Streamlit UI\napp_streamlit.py"]
    end

    subgraph "Application / Orchestration Layer"
        PIPE["LegalRAGPipeline\napp.py"]
        SAFETY["Incident Response\nSafety Guard"]
        CONF["Settings\nconfig/settings.py"]
    end

    subgraph "Intelligence Layer"
        QE["QueryExpander\nLLM-Based Slang→Statute"]
        RR["Reranker\nMS-MARCO Cross-Encoder"]
        GEN["LegalGenerator\nEvidence-First RAG"]
        VER["AnswerVerifier\nChain-of-Verification"]
    end

    subgraph "Retrieval Layer"
        VS["VectorSearcher\nHybrid (Dense + BM25)\n+ RRF Fusion"]
        EMB["Embedder\nall-MiniLM-L6-v2\n384-dim vectors"]
    end

    subgraph "Data Layer"
        CHROMA["ChromaDB\nPersistent Vector Store\n(legal_knowledge_base collection)"]
        BM25["BM25 Index\n(in-memory from ChromaDB corpus)"]
        FILES["data/\nLegal PDF Corpus (raw)"]
    end

    subgraph "Inference Backbone"
        OLLAMA["Ollama\nLlama 3.1 (8B)\nLocal LLM Server\nport: 11434"]
    end

    UI <--> PIPE
    PIPE --> SAFETY
    PIPE --> QE
    PIPE --> VS
    PIPE --> RR
    PIPE --> GEN
    PIPE --> VER
    QE <--> OLLAMA
    GEN <--> OLLAMA
    VER <--> OLLAMA
    VS --> EMB
    VS --> CHROMA
    VS --> BM25
    EMB -.-> CHROMA
    CONF -.-> PIPE
    FILES --> CHROMA
```

### 6.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| LLM Backend | Ollama (local) | Privacy — no user queries leave the machine |
| Vector Store | ChromaDB | Persistent, embedded, no external server needed |
| Embedding Model | all-MiniLM-L6-v2 | 384-dim, fast, excellent semantic similarity |
| Retrieval Strategy | Dense + BM25 via RRF | Covers both semantic and keyword-exact queries |
| Re-ranker | MS-MARCO Cross-Encoder | Highest precision for relevance scoring |
| Hallucination Guard | Chain-of-Verification (CoV) | Structural claim-by-claim evidence audit |
| Confidence Scoring | 60% CoV + 40% Reranker | Composite score balancing quality and retrieval |
| UI Framework | Streamlit | Rapid prototyping, Python-native, chat primitives |

---

## 7. Table Design

The logical table design represents the data model stored in ChromaDB's persistent collection and the in-memory operational structures.

### 7.1 ChromaDB Collection — `legal_knowledge_base`

ChromaDB stores data in a document-vector hybrid structure. The logical table mapping is:

| Column | Type | Description |
|---|---|---|
| `id` | `string` (PK) | Unique chunk identifier (e.g., `sha256_hash_chunk_0`) |
| `embedding` | `float[384]` | Dense vector from `all-MiniLM-L6-v2` |
| `document` | `string` | The cleaned text content of the chunk (≤512 tokens) |
| `metadata.source` | `string` | Source PDF filename |
| `metadata.act` | `string` | Name of the Indian statute (e.g., "Bharatiya Nyaya Sanhita 2023") |
| `metadata.section` | `string` | Section/Chapter reference within the Act |
| `metadata.pages` | `string` | Page range in the source PDF |
| `metadata.doc_id` | `string` | Parent document identifier |

### 7.2 Session State Table (Streamlit In-Memory)

| Column | Type | Description |
|---|---|---|
| `role` | `string` | `"user"` or `"assistant"` |
| `content` | `string` | Message text |
| `metadata.confidence_tier` | `string` | e.g., `"High Confidence (87.4%)"` |
| `metadata.confidence_score` | `float` | e.g., `87.4` |
| `metadata.citations` | `list[dict]` | List of citation metadata objects |
| `metadata.incident_guide` | `IncidentGuide | None` | Emergency guide dataclass or null |

### 7.3 Evaluation Results Table — `evaluation_results.csv`

| Column | Type | Description |
|---|---|---|
| `query` | `string` | Test query string |
| `expected_answer` | `string` | Ground-truth reference answer |
| `generated_answer` | `string` | System-generated answer |
| `confidence_score` | `float` | System confidence percentage |
| `confidence_tier` | `string` | Tier label |
| `citations` | `string` | JSON-serialized citation list |
| `answer_status` | `string` | `verified`, `refused`, `unavailable` |
| `precision` | `float` | Answer quality metric |
| `recall` | `float` | Evidence coverage metric |

### 7.4 Uploaded Documents Tracking (File System)

| Column | Description |
|---|---|
| Filename format | `{sha256_16char}_{original_name}.pdf` |
| Location | `data/uploads/` |
| Purpose | Deduplication (hash prefix) + citation URL serving |

---

## 8. Data-Structure Design

### 8.1 Core Data Structures

#### 8.1.1 `chunk` dictionary (Internal pipeline object)
```python
{
    "text": str,             # Cleaned text of the chunk (≤ 512 tokens)
    "metadata": {
        "source": str,       # Source PDF filename
        "act":    str,       # Indian statute name
        "section": str,      # Section/Chapter reference
        "pages":  str,       # Page range in source PDF
        "doc_id": str        # Parent document ID
    },
    "rrf_score":    float,   # Reciprocal Rank Fusion score (post-search)
    "rerank_score": float    # MS-MARCO cross-encoder score (post-rerank)
}
```

#### 8.1.2 `generation_output` dictionary (LegalGenerator output)
```python
{
    "answer":       str,        # Raw LLM-generated text with inline citations
    "citations":    list[dict], # List of metadata dicts from valid_chunks
    "valid_chunks": list[dict]  # Chunks that passed relevance threshold filter
}
```

#### 8.1.3 `final_response` dictionary (AnswerVerifier output / Pipeline return)
```python
{
    "query":                  str,
    "answer":                 str,        # Verified answer string
    "citations":              list[dict], # Citation metadata list
    "confidence_score":       float,      # 0.0 – 100.0 composite score
    "confidence_tier":        str,        # "High Confidence (87%)" etc.
    "unsupported_content_flag": bool,     # True if hallucination detected
    "verification_details":   list[dict], # Per-claim audit results
    "answer_status":          str,        # "verified" | "refused" | ...
    "incident_guide":         IncidentGuide | None
}
```

#### 8.1.4 `claims_audit` list (Chain-of-Verification result)
```python
[
    {
        "claim":     str,   # Discrete claim extracted from the draft answer
        "supported": bool   # True if directly supported by retrieved evidence
    },
    ...
]
```

#### 8.1.5 `IncidentGuide` dataclass (Safety module)
```python
@dataclass
class IncidentGuide:
    title:          str          # e.g., "Domestic Violence Immediate Steps"
    urgency_notice: str | None   # Red-alert message for life-threatening cases
    steps:          list[str]    # Ordered action steps
    resources:      list[tuple]  # [(label, url), ...]
```

### 8.2 Embedding Vector Structure

| Property | Value |
|---|---|
| Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Dimensionality | 384 floats (`float32`) |
| Normalization | L2-normalized (cosine similarity) |
| Storage | ChromaDB internal HNSW index |
| Query encoding | `model.encode([query])` → shape `(1, 384)` → `.tolist()` |

### 8.3 BM25 Index Structure

| Property | Value |
|---|---|
| Library | `rank_bm25.BM25Okapi` |
| Corpus | All documents fetched from ChromaDB at startup |
| Tokenization | Simple lowercase `.split()` |
| Persistence | In-memory only (rebuilt on each startup) |
| Output | Score array of length `len(corpus)`, top-K indices extracted |

### 8.4 RRF Fusion Dictionary

```python
fused_scores: dict[str, dict] = {
    "<chunk_id>": {
        "score":    float,   # Accumulated RRF score: Σ 1/(k + rank)
        "text":     str,     # Chunk text
        "metadata": dict     # Chunk metadata
    }
}
```

### 8.5 Confidence Scoring Formula

```
Verification Ratio   = supported_claims / total_claims
Normalized Reranker  = clamp((avg_rerank_score + 1.0) / 2.0, 0.0, 1.0)
Composite Score (%)  = ((VR × 0.60) + (NR × 0.40)) × 100
```

| Score Range | Tier |
|---|---|
| ≥ 80% | High Confidence |
| 40% – 79% | Moderate Confidence |
| < 40% | Insufficient Evidence (Refused) |
| Unsupported claim | Hallucination Detected (Refused) |

---

## 9. Deployment Diagram

### 9.1 Local Deployment (Current — Development)

```mermaid
graph TB
    subgraph "Developer Machine (Windows/Linux)"
        subgraph "Python Process — Streamlit"
            UI["Streamlit Server\nlocalhost:8501\nsrc/ui/app_streamlit.py"]
            PIPE["LegalRAGPipeline\napp.py"]
            EMB["Embedder\nall-MiniLM-L6-v2\n(~90 MB in VRAM / RAM)"]
            RR["Reranker\nMS-MARCO Cross-Encoder\n(~65 MB in RAM)"]
        end

        subgraph "Ollama Service"
            OLLAMA["Ollama Daemon\nlocalhost:11434\nLlama 3.1 8B (~4.7 GB VRAM)"]
        end

        subgraph "File System"
            CHROMA["ChromaDB\ndata/chroma_db/\n(Persistent HNSW Index)"]
            PDFS["Legal PDFs\ndata/legal_pdfs/\ndata/uploads/"]
            CONFIG["config/settings.py\n.env (API keys if any)"]
        end
    end

    BROWSER(["🌐 Browser\nlocalhost:8501"])
    BROWSER --> UI
    UI --> PIPE
    PIPE --> OLLAMA
    PIPE --> EMB
    PIPE --> RR
    PIPE --> CHROMA
    PDFS --> CHROMA
```

### 9.2 Production Deployment (Recommended Architecture)

```mermaid
graph TB
    subgraph "Client Layer"
        BROWSER(["🌐 User Browser"])
        MOBILE(["📱 Mobile Browser"])
    end

    subgraph "Reverse Proxy"
        NGINX["Nginx / Caddy\nTLS Termination\nRate Limiting"]
    end

    subgraph "Application Server (GPU Machine)"
        subgraph "Docker Container: Streamlit App"
            STREAM["Streamlit Server\n:8501"]
            PIPE2["LegalRAGPipeline"]
        end
        subgraph "Docker Container: Ollama"
            OLLAMA2["Ollama\nLlama 3.1 8B\n:11434\nGPU: CUDA / ROCm"]
        end
    end

    subgraph "Storage"
        CHROMADB2["ChromaDB Volume\n/data/chroma_db"]
        PDFVOL["PDF Volume\n/data/legal_pdfs"]
    end

    BROWSER --> NGINX
    MOBILE --> NGINX
    NGINX --> STREAM
    STREAM --> PIPE2
    PIPE2 --> OLLAMA2
    PIPE2 --> CHROMADB2
    PDFVOL --> CHROMADB2
```

### 9.3 Deployment Configuration Summary

| Component | Local Dev | Production |
|---|---|---|
| Web Server | `streamlit run` | Docker + Nginx reverse proxy |
| LLM Server | `ollama serve` (local daemon) | Ollama in Docker with GPU passthrough |
| Vector DB | ChromaDB PersistentClient (file) | ChromaDB volume-mounted in Docker |
| Embedding Model | Loaded in Python process RAM | Same (model weights in container) |
| Cross-Encoder | Loaded in Python process RAM | Same |
| PDF Storage | `data/` folder (local) | Docker volume / cloud object storage |
| Auth | None | Streamlit Authenticator / Nginx Basic Auth |
| HTTPS | None | Let's Encrypt via Caddy / Nginx |
| Hardware (Minimum) | 16 GB RAM, 8 GB VRAM | 32 GB RAM, 16 GB VRAM (A10/RTX 4090) |

### 9.4 System Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores | 8+ cores |
| RAM | 16 GB | 32 GB |
| GPU VRAM | 6 GB (Llama 3.1 4-bit quantized) | 16 GB (Llama 3.1 8B full) |
| Disk | 20 GB | 50 GB |
| OS | Windows 10 / Ubuntu 20.04 | Ubuntu 22.04 LTS |
| Python | 3.10+ | 3.11+ |
| Ollama | v0.2.0+ | Latest |

---

*Document prepared for: Nyaya — Indian Legal RAG Assistant*
*Project: Indian Legal Knowledge System | System Analysis and Design Report*
