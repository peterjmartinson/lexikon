def load_text(filepath: str) -> str:
    """Load a text file and return its contents as a UTF-8 string."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
