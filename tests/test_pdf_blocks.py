from pathlib import Path
import pymupdf


def main():

    pdf_path = next(
        Path("data/raw").glob(
            "*Bharatiya Nyaya Sanhita*.pdf"
        )
    )

    print(f"Testing: {pdf_path.name}")

    document = pymupdf.open(str(pdf_path))

    for page_number in range(min(3, len(document))):

        page = document[page_number]

        print("\n" + "=" * 100)
        print(f"PAGE {page_number + 1}")
        print("=" * 100)

        blocks = page.get_text(
            "blocks"
        )

        for index, block in enumerate(blocks):

            x0, y0, x1, y1, text = block[:5]

            print("\n" + "-" * 80)
            print(f"BLOCK {index}")
            print(
                f"x0={x0:.1f}, "
                f"y0={y0:.1f}, "
                f"x1={x1:.1f}, "
                f"y1={y1:.1f}"
            )
            print(repr(text))


    document.close()


if __name__ == "__main__":
    main()