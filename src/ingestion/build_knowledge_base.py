from pathlib import Path
import hashlib

import chromadb

from config.settings import (
    CHROMA_DB_DIR,
    RAW_DATA_DIR,
    COLLECTION_NAME,
)

from src.embeddings.embedder import Embedder
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_cleaner import clean_text
from src.ingestion.chunker import chunk_pages


# Map filename keywords → short Act label.
# Keys are substrings matched case-insensitively against the PDF filename.
ACT_MAP = {
    # -- Indian Criminal Law (original) --
    "Bharatiya Nyaya Sanhita": "BNS",
    "Bharatiya Nagarik Suraksha Sanhita": "BNSS",
    "Bharatiya Sakshya Adhiniyam": "BSA",

    # -- Civil / Contract --
    "Indian Contract Act": "Contract Act 1872",
    "Specific Relief": "Specific Relief Act 1963",
    "Limitation Act": "Limitation Act 1963",
    "Negotiable Instruments": "Negotiable Instruments Act 1881",
    "Arbitration": "Arbitration and Conciliation Act 1996",

    # -- Property --
    "Transfer of Property": "Transfer of Property Act 1882",
    "Registration Act": "Registration Act 1908",
    "Land Acquisition": "Land Acquisition Act",

    # -- Family / Personal Law --
    "Hindu Marriage": "Hindu Marriage Act 1955",
    "Hindu Succession": "Hindu Succession Act 1956",
    "Hindu Minority": "Hindu Minority and Guardianship Act 1956",
    "Hindu Adoption": "Hindu Adoptions and Maintenance Act 1956",
    "Indian Succession": "Indian Succession Act 1925",
    "Guardians and Wards": "Guardians and Wards Act 1890",
    "Dissolution of Muslim": "Dissolution of Muslim Marriages Act 1939",
    "Dowry Prohibition": "Dowry Prohibition Act 1961",
    "Protection of Women": "Protection of Women from Domestic Violence Act 2005",

    # -- Consumer / RTI / Digital --
    "Consumer Protection": "Consumer Protection Act 2019",
    "Right to Information": "RTI Act 2005",
    "Information Technology": "IT Act 2000",

    # -- Labour --
    "Factories Act": "Factories Act 1948",
    "Industrial Disputes": "Industrial Disputes Act 1947",
    "Minimum Wages": "Minimum Wages Act 1948",
    "Employees Provident": "EPF Act 1952",
    "Payment of Gratuity": "Payment of Gratuity Act 1972",
    "Maternity Benefit": "Maternity Benefit Act 1961",

    # -- Corporate / Insolvency --
    "Companies Act": "Companies Act 2013",
    "Insolvency and Bankruptcy": "IBC 2016",
    "Partnership Act": "Indian Partnership Act 1932",
    "LLP Act": "LLP Act 2008",

    # -- Intellectual Property --
    "Copyright": "Copyright Act 1957",
    "Trade Marks": "Trade Marks Act 1999",
    "Patents Act": "Patents Act 1970",
    "Designs Act": "Designs Act 2000",
    "Geographical Indications": "GI Act 1999",

    # -- Environment --
    "Environment Protection": "Environment Protection Act 1986",
    "Wildlife Protection": "Wildlife Protection Act 1972",
    "Forest Conservation": "Forest Conservation Act 1980",

    # -- Tax --
    "Income Tax": "Income Tax Act 1961",
    "Goods and Services Tax": "GST Act 2017",
    "Customs Act": "Customs Act 1962",

    # -- Transport --
    "Motor Vehicles": "Motor Vehicles Act 1988",

    # -- Constitutional / Administrative --
    "Constitution of India": "Constitution of India",

    # -- Legacy / Old Acts --
    "Indian Penal Code": "IPC 1860",
    "Code of Criminal Procedure": "CrPC 1973",
    "Indian Evidence": "Indian Evidence Act 1872",
}


def get_act_name(filename: str) -> str:
    """
    Extract an Act label from the PDF filename.
    Tries ACT_MAP keys (case-insensitive) first; falls back to a cleaned
    version of the filename stem so no document is ever tagged UNKNOWN_ACT.
    """
    lower = filename.lower()
    for key, act in ACT_MAP.items():
        if key.lower() in lower:
            return act
    # Graceful fallback: derive a readable label from the filename stem.
    stem = Path(filename).stem
    readable = stem.replace("_", " ").replace("-", " ").strip()
    return readable if readable else "Unknown Act"


def index_pdf_file(
    pdf_path: Path,
    collection,
    embedder: Embedder,
    source_name: str | None = None,
    act_name: str | None = None,
    document_id_prefix: str | None = None,
    use_legacy_ids: bool = False,
) -> int:
    """Extract, chunk, embed, and upsert one PDF into an existing collection."""
    source_name = source_name or pdf_path.name
    act_abbreviation = act_name or get_act_name(source_name)
    pages = load_pdf(str(pdf_path))

    cleaned_pages = [
        {"page_number": page["page_number"], "text": cleaned_text}
        for page in pages
        if (cleaned_text := clean_text(page["text"])).strip()
    ]
    chunks = chunk_pages(cleaned_pages, act_name=act_abbreviation)

    if not chunks:
        return 0

    if document_id_prefix is None:
        document_id_prefix = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]

    document_chunks = []
    document_metadata = []
    document_ids = []
    for index, chunk in enumerate(chunks):
        metadata = {
            "source": source_name,
            "act": chunk.get("act", act_abbreviation),
            "section": str(chunk.get("section_num", "Unknown")),
            "chunk_index": chunk.get("chunk_index", 0),
            "pages": ",".join(str(page) for page in sorted(chunk["pages"])),
        }
        document_chunks.append(chunk["text"])
        document_metadata.append(metadata)
        if use_legacy_ids:
            document_ids.append(
                f"{document_id_prefix}_SEC_{metadata['section']}_GLOBAL_{index}"
            )
        else:
            document_ids.append(
                f"{document_id_prefix}_SEC_{metadata['section']}_CHUNK_{index}"
            )

    embeddings = embedder.encode_documents(document_chunks)
    collection.upsert(
        ids=document_ids,
        documents=document_chunks,
        embeddings=embeddings.tolist(),
        metadatas=document_metadata,
    )
    return len(document_chunks)


def index_uploaded_pdf(pdf_path: Path, source_name: str, act_name: str) -> int:
    """Index an uploaded PDF and return the number of chunks stored."""
    embedder = Embedder()
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Indian law corpus"},
    )
    file_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]
    return index_pdf_file(
        pdf_path=pdf_path,
        collection=collection,
        embedder=embedder,
        source_name=source_name,
        act_name=act_name,
        document_id_prefix=f"UPLOAD_{file_hash}",
    )


def build_knowledge_base():
    """Build the ChromaDB knowledge base from all legal PDFs in data/raw/."""

    print("Initializing embedding model...")
    embedder = Embedder()

    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Indian law corpus"
        },
    )

    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in: {RAW_DATA_DIR}"
        )

    total_chunks = 0

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        act_label = get_act_name(pdf_path.name)
        print(f"  Detected act: {act_label}")
        stored_chunks = index_pdf_file(
            pdf_path=pdf_path,
            collection=collection,
            embedder=embedder,
            document_id_prefix=act_label.replace(" ", "_")[:20],
            use_legacy_ids=True,
        )

        if not stored_chunks:
            print("  No usable text found.")
            continue

        total_chunks += stored_chunks

        print(
            f"  Stored {stored_chunks} chunks "
            f"from {pdf_path.name}"
        )

    print("\nKnowledge base construction complete.")
    print(f"Total chunks stored: {total_chunks}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Database: {CHROMA_DB_DIR}")


if __name__ == "__main__":
    build_knowledge_base()
