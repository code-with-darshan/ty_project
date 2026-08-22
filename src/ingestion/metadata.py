from pathlib import Path

def create_metadata(
    source_path: str,
    page_numbers: list[int],
    act_name: str,
    section_num: str = None,
) -> dict:
    """Create structural metadata for a legal document chunk."""
    
    source = Path(source_path)
    
    return {
        "source": source.name,
        "act": act_name,
        "section": section_num or "Unknown",
        "pages": page_numbers,
    }