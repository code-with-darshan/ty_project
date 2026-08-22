import re

def clean_text(text: str) -> str:
    """
    Cleans raw PDF text by removing Gazette artifacts, fixing line breaks, 
    and normalizing spaces to provide pristine RAG context.
    """
    if not text:
        return ""

    # 1. Remove headers/footers FIRST while newlines still exist.
    # Using re.MULTILINE ensures ^ and $ match line boundaries, preventing 
    # the regex from eating the rest of the page.
    patterns_to_remove = [
        r"THE GAZETTE OF INDIA EXTRAORDINARY",
        r"^\s*\d*\s*\[?PART II(?:—|-).*?(?:\]|$)",  # Safely catches even-page headers
        r"^\s*Sec\. 1\]\s*\d*",                     # Safely catches odd-page headers
        r"REGISTERED NO\. DL(?:—|-).*?2003(?:—|-)23",
        r"xxxGID(?:H|E)xxx",
        r"CG-DL-E-\d+-\d+",
        r"jftLVªh lañ Mhñ.*?(?=PART|$)", 
        r"vlk/kkj\.k Hkkx.*?(?=PART|$)",
        r"izkf/kdkj ls izdkf'kr",
        r"lañ \d+\..*?¼'kd½", 
        r"No\. \d+\..*?\(SAKA\)", 
        r"bl Hkkx esa.*?tk ldsA",
        r"Separate paging is given.*?compilation\.",
        r"MINISTRY OF LAW\s*AND JUSTICE",
        r"New Delhi, the.*?\d{4}",
        r"The following Act of Parliament.*?general information:—",
        r"_{10,}",  
        r"MGIPMRND.*?",
        r"UPLOADED BY THE MANAGER.*?",
        r"AND PUBLISHED BY THE CONTROLLER.*?"
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.MULTILINE)

    # 2. NOW replace newlines with spaces to prevent cross-line word merging
    text = text.replace('\n', ' ')

    # 3. Quick fixes for the squished words caused by the PDF's print kerning
    word_fixes = {
        "ThisAct": "This Act",
        "intoforce": "into force",
        "bynotification": "by notification",
        "therewithor": "therewith or",
        "incidentalthereto": "incidental thereto"
    }
    for bad_word, good_word in word_fixes.items():
        text = text.replace(bad_word, good_word)

    # 4. Clean up all the resulting double/triple spaces left behind
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()