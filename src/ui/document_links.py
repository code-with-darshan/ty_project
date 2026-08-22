"""Publish locally indexed PDFs for citation links in the Streamlit UI."""

from hashlib import sha256
from pathlib import Path
from shutil import copy2
from urllib.parse import quote

from config.settings import RAW_DATA_DIR, STATIC_DOCUMENTS_DIR, UPLOADS_DIR


def _find_source_file(source_name: str) -> Path | None:
    """Resolve a citation source name to a PDF owned by this project."""
    safe_name = Path(source_name).name
    if safe_name != source_name or Path(safe_name).suffix.lower() != ".pdf":
        return None

    raw_file = RAW_DATA_DIR / safe_name
    if raw_file.is_file():
        return raw_file

    if UPLOADS_DIR.is_dir():
        for uploaded_file in UPLOADS_DIR.iterdir():
            if uploaded_file.is_file() and uploaded_file.name.endswith(f"_{safe_name}"):
                return uploaded_file
    return None


def citation_pdf_url(citation: dict) -> str | None:
    """Return a local static-PDF URL for a citation, including its first page."""
    source_file = _find_source_file(str(citation.get("source", "")))
    if source_file is None:
        return None

    file_digest = sha256(source_file.read_bytes()).hexdigest()[:12]
    published_name = f"{file_digest}_{source_file.name}"
    published_file = STATIC_DOCUMENTS_DIR / published_name
    STATIC_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    if (
        not published_file.exists()
        or published_file.stat().st_size != source_file.stat().st_size
    ):
        copy2(source_file, published_file)

    first_page = str(citation.get("pages", "")).split(",")[0].strip()
    page_fragment = f"#page={first_page}" if first_page.isdigit() else ""
    return f"/app/static/documents/{quote(published_name)}{page_fragment}"
