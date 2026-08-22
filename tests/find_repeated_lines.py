from collections import Counter
from pathlib import Path

from src.ingestion.pdf_loader import load_pdf


def main():

    pdf_path = next(
        Path("data/raw").glob(
            "*Bharatiya Nyaya Sanhita*.pdf"
        )
    )

    print(f"Testing: {pdf_path.name}")

    pages = load_pdf(str(pdf_path))

    counter = Counter()

    for page in pages:

        lines = page["text"].splitlines()

        for line in lines:

            line = line.strip()

            if line:
                counter[line] += 1

    print("\nMost repeated lines:\n")

    for line, count in counter.most_common(30):

        if count >= 3:

            print(
                f"{count:3}x | {line}"
            )


if __name__ == "__main__":
    main()