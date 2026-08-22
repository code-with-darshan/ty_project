import pymupdf


def load_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF while preserving page information.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text(
            "text",
            sort=True
        )

        if text.strip():

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    document.close()

    return pages