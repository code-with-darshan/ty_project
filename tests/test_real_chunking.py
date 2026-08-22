from pathlib import Path

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_cleaner import clean_text
from src.ingestion.chunker import chunk_pages


def main():

    pdf_path = next(
        Path("data/raw").glob("*Bharatiya Nyaya Sanhita*.pdf")
    )

    print(f"Testing PDF: {pdf_path.name}")

    pages = load_pdf(str(pdf_path))

    total_chunks = 0

    for page in pages[:10]:

        text = clean_text(page["text"])
        chunks = chunk_pages([{"page_number": page["page_number"], "text": text}], act_name="BNS")

        print(
            f"\nPage {page['page_number']}: "
            f"{len(chunks)} chunks"
        )

        for index, chunk in enumerate(chunks[:3], start=1):

            preview = chunk["text"].replace("\n", " ")[:200]

            print(
                f"  Chunk {index}: {preview}..."
            )

        total_chunks += len(chunks)

    print(
        f"\nTotal chunks in first 10 pages: "
        f"{total_chunks}"
    )


if __name__ == "__main__":
    main()
