import os

import pytest

from lexikon.loader import load_text

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_load_text_returns_string():
    path = os.path.join(FIXTURES_DIR, "gutenberg_sample.txt")
    text = load_text(path)
    assert isinstance(text, str)
    assert len(text) > 0


def test_load_text_contains_expected_content():
    path = os.path.join(FIXTURES_DIR, "gutenberg_sample.txt")
    text = load_text(path)
    assert "professeur" in text


def test_load_text_raises_for_missing_file():
    with pytest.raises(FileNotFoundError):
        load_text("/nonexistent/path/does_not_exist.txt")
