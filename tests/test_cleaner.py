import os

from lexikon.cleaner import (
    filter_short_tokens,
    remove_punctuation_normalize,
    strip_gutenberg_noise,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

_WITH_MARKERS = """\
Project Gutenberg header text.
*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE ***
Le professeur était impatient.
*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE ***
End of Project Gutenberg EBook."""

_WITHOUT_MARKERS = "Le professeur était impatient."


class TestStripGutenbergNoise:
    def test_strips_header_and_footer(self):
        result = strip_gutenberg_noise(_WITH_MARKERS)
        assert "Project Gutenberg header" not in result
        assert "End of Project Gutenberg EBook" not in result
        assert "professeur" in result

    def test_falls_back_when_no_markers(self):
        result = strip_gutenberg_noise(_WITHOUT_MARKERS)
        assert result == _WITHOUT_MARKERS

    def test_uses_fixture_file(self):
        path = os.path.join(FIXTURES_DIR, "gutenberg_sample.txt")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        result = strip_gutenberg_noise(text)
        assert "professeur" in result
        assert "Project Gutenberg" not in result


class TestRemovePunctuationNormalize:
    def test_removes_common_punctuation(self):
        result = remove_punctuation_normalize("Hello, world! It fine.")
        assert "," not in result
        assert "!" not in result
        assert "." not in result

    def test_normalizes_whitespace(self):
        result = remove_punctuation_normalize("word   another  word")
        assert result == "word another word"

    def test_handles_french_guillemets(self):
        result = remove_punctuation_normalize("«Bonjour» dit-il.")
        assert "«" not in result
        assert "»" not in result

    def test_returns_stripped_string(self):
        result = remove_punctuation_normalize("  hello  ")
        assert result == result.strip()


class TestFilterShortTokens:
    def test_filters_single_chars(self):
        result = filter_short_tokens(["a", "be", "hello", "I", "it"])
        assert "a" not in result
        assert "I" not in result
        assert "be" in result
        assert "hello" in result

    def test_default_min_length_is_two(self):
        result = filter_short_tokens(["x", "ab"])
        assert result == ["ab"]

    def test_custom_min_length(self):
        result = filter_short_tokens(["ab", "abc", "abcd"], min_length=3)
        assert "ab" not in result
        assert "abc" in result
        assert "abcd" in result

    def test_empty_list(self):
        assert filter_short_tokens([]) == []
