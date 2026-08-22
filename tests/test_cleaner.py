from pathlib import Path

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_cleaner import clean_text


def main():

    pdf_path = next(
        Path("data/raw").glob(
            "*Bharatiya Nyaya Sanhita*.pdf"
        )
    )

    print(f"Testing: {pdf_path.name}")

    pages = load_pdf(str(pdf_path))

    for page in pages[:3]:

        cleaned = clean_text(
            page["text"]
        )

        print("\n" + "=" * 70)
        print(
            f"PAGE {page['page_number']}"
        )
        print("=" * 70)

        print(
            cleaned[:2000]
        )


if __name__ == "__main__":
    main()