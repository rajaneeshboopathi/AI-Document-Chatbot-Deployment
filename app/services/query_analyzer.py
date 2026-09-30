import re


# ------------------------------------------------------------
# Common spelling / wording normalization
# ------------------------------------------------------------

SPELLING_REPLACEMENTS = {
    "whats": "what is",
    "wat": "what",
    "wht": "what",
    "abt": "about",
    "mentiond": "mentioned",
    "langauge": "language",
    "langauges": "languages",
    "technolgies": "technologies",
    "technolgy": "technology",
}


def normalize_text(text):
    """
    Normalizes user input for easier query analysis.
    """

    text = text.lower().strip()

    # Remove punctuation at the end
    text = re.sub(r"[!?.,]+$", "", text)

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Basic spelling replacements
    for wrong, correct in SPELLING_REPLACEMENTS.items():
        text = re.sub(
            rf"\b{re.escape(wrong)}\b",
            correct,
            text,
        )

    return text


# ------------------------------------------------------------
# Page number extraction
# ------------------------------------------------------------

def extract_page_range(question):
    """
    Detects page references such as:

        page 2
        page 2-3
        pages 2 to 3
        pages 2 through 3
        from page 2 to page 3
        between pages 2 and 3

    Returns:

        (page_start, page_end)

    Examples:

        "what is on page 2"
            -> (2, 2)

        "what is on pages 2 to 3"
            -> (2, 3)

        No page reference
            -> (None, None)
    """

    text = normalize_text(question)

    # --------------------------------------------------------
    # Page range
    # --------------------------------------------------------

    range_patterns = [
        r"\bpages?\s+(\d+)\s*(?:-|–|—|to|through)\s*(?:page\s*)?(\d+)\b",

        r"\bfrom\s+page\s+(\d+)\s+to\s+(?:page\s+)?(\d+)\b",

        r"\bbetween\s+pages?\s+(\d+)\s+and\s+(\d+)\b",
    ]

    for pattern in range_patterns:
        match = re.search(pattern, text)

        if match:
            page_start = int(match.group(1))
            page_end = int(match.group(2))

            # Make sure the range is always ascending
            if page_start > page_end:
                page_start, page_end = page_end, page_start

            return page_start, page_end

    # --------------------------------------------------------
    # Single page
    # --------------------------------------------------------

    single_page_patterns = [
        r"\bpage\s+(\d+)\b",
    ]

    for pattern in single_page_patterns:
        match = re.search(pattern, text)

        if match:
            page = int(match.group(1))
            return page, page

    return None, None


# ------------------------------------------------------------
# Remove page instruction from semantic search query
# ------------------------------------------------------------

def clean_page_reference(question):
    """
    Removes page-selection wording from the question.

    Example:

        "what technologies are mentioned in page 2"

    becomes approximately:

        "what technologies are mentioned in"
    """

    text = normalize_text(question)

    patterns = [
        r"\bfrom\s+page\s+\d+\s+to\s+(?:page\s+)?\d+\b",
        r"\bbetween\s+pages?\s+\d+\s+and\s+\d+\b",
        r"\bpages?\s+\d+\s*(?:-|–|—|to|through)\s*(?:page\s*)?\d+\b",
        r"\bpage\s+\d+\b",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    # Clean leftover wording
    text = re.sub(r"\s+", " ", text).strip()

    # Remove common trailing connectors
    text = re.sub(
        r"\b(in|on|from|of|for)\s*$",
        "",
        text,
    ).strip()

    return text


# ------------------------------------------------------------
# Detect broad page questions
# ------------------------------------------------------------

def is_broad_page_query(question):
    """
    Determines whether the user is asking for a general
    summary/description of a specific page or page range.
    """

    text = normalize_text(question)

    broad_patterns = [
        r"\bwhat is mentioned\b",
        r"\bwhat is on\b",
        r"\bwhat does .* say\b",
        r"\bwhat does .* contain\b",
        r"\bwhat is covered\b",
        r"\bsummarize\b",
        r"\bsummary\b",
        r"\bdescribe\b",
        r"\bexplain\b",
        r"\btell me about\b",
    ]

    return any(re.search(pattern, text) for pattern in broad_patterns)


# ------------------------------------------------------------
# Main query analyzer
# ------------------------------------------------------------

def analyze_query(question):
    """
    Returns structured information about the user's question.

    Example:

        {
            "original_question": "...",
            "normalized_question": "...",
            "search_query": "...",
            "page_start": 2,
            "page_end": 3,
            "query_type": "broad_page"
        }
    """

    normalized_question = normalize_text(question)

    page_start, page_end = extract_page_range(
        normalized_question
    )

    search_query = clean_page_reference(
        normalized_question
    )

    if page_start is not None:
        if is_broad_page_query(normalized_question):
            query_type = "broad_page"
        else:
            query_type = "page_specific"
    else:
        query_type = "normal"

    return {
        "original_question": question,
        "normalized_question": normalized_question,
        "search_query": search_query,
        "page_start": page_start,
        "page_end": page_end,
        "query_type": query_type,
    }