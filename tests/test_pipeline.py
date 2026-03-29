"""End-to-end pipeline integration test using a minimal Gutenberg fixture.

spaCy and the translation client are both mocked so the test runs without
model downloads or network access.
"""
import os
from unittest.mock import MagicMock, patch

from lexikon.cleaner import (
    filter_short_tokens,
    remove_punctuation_normalize,
    strip_gutenberg_noise,
)
from lexikon.lemmatizer import LemmaEntry, deduplicate_sort
from lexikon.loader import load_text
from lexikon.writer import write_lexicon

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _make_token(lemma: str, pos: str, *, is_alpha: bool = True, is_stop: bool = False):
    token = MagicMock()
    token.lemma_ = lemma
    token.pos_ = pos
    token.is_alpha = is_alpha
    token.is_stop = is_stop
    token.morph.get.return_value = []
    return token


class TestPipeline:
    def test_gutenberg_noise_stripped_before_lemmatization(self, tmp_path):
        fixture_path = os.path.join(FIXTURES_DIR, "gutenberg_sample.txt")
        text = load_text(fixture_path)
        text = strip_gutenberg_noise(text)
        assert "Project Gutenberg" not in text
        assert "professeur" in text

    def test_end_to_end_with_mocked_nlp_and_translator(self, tmp_path):
        fixture_path = os.path.join(FIXTURES_DIR, "gutenberg_sample.txt")

        # --- loading & cleaning ---
        text = load_text(fixture_path)
        text = strip_gutenberg_noise(text)
        text = remove_punctuation_normalize(text)
        tokens = filter_short_tokens(text.split())
        clean_text = " ".join(tokens)

        # Gutenberg boilerplate must be gone
        assert "Project Gutenberg" not in clean_text

        # --- lemmatization (mocked) ---
        mock_doc = [
            _make_token("professeur", "NOUN"),
            _make_token("voyager", "VERB"),
            _make_token("impatient", "ADJ"),
        ]
        mock_nlp = MagicMock(return_value=mock_doc)

        with patch("lexikon.lemmatizer.spacy.load", return_value=mock_nlp):
            from lexikon.lemmatizer import extract_lemma_entries

            entries = extract_lemma_entries(clean_text)

        entries = deduplicate_sort(entries)

        assert len(entries) == 3
        assert entries[0].lemma == "impatient"  # sorted first

        # --- translation (pre-canned, no API call) ---
        translations = {
            "impatient": "impatient",
            "professeur": "professor",
            "voyager": "to travel",
        }

        # --- output ---
        output_file = tmp_path / "lexikon_output.txt"
        write_lexicon(entries, translations, str(output_file))

        content = output_file.read_text(encoding="utf-8")
        assert "impatient (adjective) - impatient" in content
        assert "professeur (noun) - professor" in content
        assert "voyager (verb) - to travel" in content

        # verify sorted order
        all_lines = content.strip().splitlines()
        entry_lines = [l for l in all_lines if not l.startswith("---")]
        assert entry_lines[0].startswith("impatient")
        assert entry_lines[1].startswith("professeur")
        assert entry_lines[2].startswith("voyager")
