import re
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

# Matches and CAPTURES the section number (e.g., "103")
SECTION_PATTERN = re.compile(r"(?<![a-zA-Z0-9])(\d{1,3})\.\s+(?=[A-Z\(])")

def split_into_sections(text: str) -> list[dict]:
    """
    Split legal text and extract the specific section number.
    Returns a list of dicts containing the section number and text.
    """
    matches = list(SECTION_PATTERN.finditer(text))
    
    if not matches:
        return [{"section_num": "Unknown", "text": text.strip()}] if text.strip() else []

    sections = []

    # Preserve text before the first numbered section (Preamble/Chapters)
    if matches[0].start() > 0:
        preamble = text[:matches[0].start()].strip()
        if preamble:
            sections.append({"section_num": "Preamble", "text": preamble})

    for index, match in enumerate(matches):
        section_num = match.group(1) # Extracts the actual number
        start = match.start()
        
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)
            
        section_text = text[start:end].strip()
        if section_text:
            sections.append({"section_num": section_num, "text": section_text})

    return sections


def split_large_text(text: str) -> list[str]:
    """
    Split an oversized legal section into chunks by sentences to avoid 
    cutting rules in half.
    """
    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []
    # Split by period followed by a space
    sentences = re.split(r'(?<=\.)\s', text)
    
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > CHUNK_SIZE and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
        else:
            current_chunk += sentence + " "
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks


def chunk_pages(pages: list[dict], act_name: str = "Unknown") -> list[dict]:
    """
    Combine pages into chunks and assign persistent metadata.
    """
    chunks = []
    current_section_num = None
    current_section_text = ""
    current_section_pages = set()

    for page in pages:
        text = page["text"]
        page_num = page["page_number"]
        
        matches = list(SECTION_PATTERN.finditer(text))
        
        if not matches:
            current_section_text += " " + text
            current_section_pages.add(page_num)
            continue
            
        start_idx = 0
        for match in matches:
            pre_text = text[start_idx:match.start()].strip()
            if pre_text:
                current_section_text += " " + pre_text
                current_section_pages.add(page_num)
                
            if current_section_text.strip():
                sub_chunks = split_large_text(current_section_text)
                for i, sub_chunk in enumerate(sub_chunks):
                    chunks.append({
                        "act": act_name,
                        "section_num": current_section_num,
                        "chunk_index": i,
                        "pages": list(current_section_pages),
                        "text": sub_chunk
                    })
            
            # Reset for the new section
            current_section_num = match.group(1)
            current_section_text = ""
            current_section_pages = {page_num}
            start_idx = match.start()
            
        current_section_text += " " + text[start_idx:].strip()

    if current_section_text.strip():
        sub_chunks = split_large_text(current_section_text)
        for i, sub_chunk in enumerate(sub_chunks):
            chunks.append({
                "act": act_name,
                "section_num": current_section_num,
                "chunk_index": i,
                "pages": list(current_section_pages),
                "text": sub_chunk
            })

    return chunks