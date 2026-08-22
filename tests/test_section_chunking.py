from pathlib import Path

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_cleaner import clean_text
from src.ingestion.chunker import chunk_pages


def main():
    pdf_path = next(Path("data/raw").glob("*Bharatiya Nyaya Sanhita*.pdf"))
    print(f"Testing: {pdf_path.name}")

    pages = load_pdf(str(pdf_path))
    cleaned_pages = []

    for page in pages:
        text = clean_text(page["text"])
        if text.strip():
            cleaned_pages.append(
                {
                    "page_number": page["page_number"],
                    "text": text,
                }
            )

    # Pass the act name to populate the metadata correctly
    chunks = chunk_pages(cleaned_pages, act_name="BNS")

    print(f"\nTotal legal chunks: {len(chunks)}")
    print("\nFirst 15 chunks:")

    for index, chunk in enumerate(chunks[:15], start=1):
        print("\n" + "=" * 70)
        print(f"Chunk {index}")
        print(f"Act: {chunk.get('act', 'Unknown')}")
        print(f"Section Number: {chunk.get('section_num', 'Unknown')}")
        print(f"Pages: {chunk.get('pages', [])}")
        print("=" * 70)
        print(chunk["text"][:500])


if __name__ == "__main__":
    main()