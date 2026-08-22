from src.ingestion.chunker import chunk_pages


def main():

    sample = """
1. Short first provision.

2. Short second provision.

103. Whoever commits murder shall be punished with death
or imprisonment for life, and shall also be liable to fine.

104. Whoever commits an offence under this section shall
be punished according to the provisions of this Sanhita.
"""

    chunks = chunk_pages([{"page_number": 1, "text": sample}], act_name="BNS")

    print(f"Chunks created: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print("\n" + "=" * 60)
        print(f"CHUNK {index}")
        print("=" * 60)
        print(chunk["text"])


if __name__ == "__main__":
    main()
