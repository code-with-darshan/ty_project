from pathlib import Path

import pymupdf


def main():

    pdf_path = next(
        Path("data/raw").glob(
            "*Bharatiya Nyaya Sanhita*.pdf"
        )
    )

    document = pymupdf.open(
        str(pdf_path)
    )

    print(
        f"Testing: {pdf_path.name}"
    )

    for page_number in [1, 2, 3]:

        page = document[
            page_number - 1
        ]

        print(
            "\n" + "=" * 80
        )

        print(
            f"PAGE {page_number}"
        )

        print(
            "=" * 80
        )

        blocks = page.get_text(
            "blocks"
        )

        for block in blocks:

            text = block[4].strip()

            if text:

                print(
                    "\n--- BLOCK ---"
                )

                print(text[:1000])

    document.close()


if __name__ == "__main__":
    main()