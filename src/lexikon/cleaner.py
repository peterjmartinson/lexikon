import re


def strip_gutenberg_noise(text: str) -> str:
    """Remove Project Gutenberg header and footer from text.

    Strips everything before the '*** START OF ...' marker and after
    the '*** END OF ...' marker. Falls back to the original text if
    the markers are absent.
    """
    start_match = re.search(r"\*{3}\s*START OF[^\*]*\*{3}", text, re.IGNORECASE)
    end_match = re.search(r"\*{3}\s*END OF[^\*]*\*{3}", text, re.IGNORECASE)
    if start_match and end_match:
        return text[start_match.end() : end_match.start()].strip()
    return text.strip()


def remove_punctuation_normalize(text: str) -> str:
    """Replace punctuation with spaces and collapse multiple whitespace to one."""
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def filter_short_tokens(tokens: list[str], min_length: int = 2) -> list[str]:
    """Return only tokens whose length is at least *min_length*."""
    return [t for t in tokens if len(t) >= min_length]
