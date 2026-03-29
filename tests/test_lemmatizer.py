import pytest
from unittest.mock import MagicMock, patch

from lexikon.lemmatizer import (
    EXCLUDED_POS,
    LANGUAGE_MODEL_MAP,
    LemmaEntry,
    deduplicate_sort,
    extract_lemma_entries,
)


def _make_token(lemma: str, pos: str, *, is_alpha: bool = True, is_stop: bool = False, gender: str | None = None):
    token = MagicMock()
    token.lemma_ = lemma
    token.pos_ = pos
    token.is_alpha = is_alpha
    token.is_stop = is_stop
    token.morph.get.return_value = [gender] if gender else []
    return token


class TestConstants:
    def test_french_model_mapped(self):
        assert "fr" in LANGUAGE_MODEL_MAP
        assert LANGUAGE_MODEL_MAP["fr"] == "fr_core_news_md"

    def test_excluded_pos_contains_noise_tags(self):
        for tag in ("PUNCT", "SPACE", "NUM", "DET", "ADP"):
            assert tag in EXCLUDED_POS


class TestExtractLemmaEntries:
    def _nlp(self, tokens):
        return MagicMock(return_value=tokens)

    def test_returns_lemma_entries_for_content_words(self):
        nlp = self._nlp([_make_token("manger", "VERB")])
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("manger")
        assert len(result) == 1
        assert result[0].lemma == "manger"
        assert result[0].pos == "VERB"

    def test_filters_excluded_pos(self):
        nlp = self._nlp(
            [
                _make_token("manger", "VERB"),
                _make_token(".", "PUNCT", is_alpha=False),
                _make_token("le", "DET"),
            ]
        )
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("le manger.")
        lemmas = [e.lemma for e in result]
        assert "manger" in lemmas
        assert "." not in lemmas
        assert "le" not in lemmas

    def test_filters_stop_words(self):
        nlp = self._nlp(
            [
                _make_token("manger", "VERB"),
                _make_token("le", "NOUN", is_stop=True),
            ]
        )
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("le manger")
        assert len(result) == 1
        assert result[0].lemma == "manger"

    def test_filters_non_alpha_tokens(self):
        nlp = self._nlp(
            [
                _make_token("manger", "VERB"),
                _make_token("42", "NUM", is_alpha=False),
            ]
        )
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("42 manger")
        assert len(result) == 1

    def test_lemma_lowercased(self):
        nlp = self._nlp([_make_token("Manger", "VERB")])
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("Manger")
        assert result[0].lemma == "manger"

    def test_filters_single_char_lemmas(self):
        nlp = self._nlp([_make_token("a", "VERB")])
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("a")
        assert result == []

    def test_raises_for_unsupported_language(self):
        with pytest.raises(ValueError, match="Unsupported language"):
            extract_lemma_entries("text", lang="zz")

    def test_filters_proper_nouns(self):
        nlp = self._nlp([_make_token("Jules", "PROPN")])
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("Jules")
        assert result == []

    def test_captures_gender_from_morph(self):
        nlp = self._nlp([_make_token("professeur", "NOUN", gender="Masc")])
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("professeur")
        assert result[0].gender == "Masc"

    def test_gender_none_when_absent(self):
        nlp = self._nlp([_make_token("manger", "VERB")])
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("manger")
        assert result[0].gender is None

    def test_allows_duplicates(self):
        """extract_lemma_entries does not deduplicate; that is deduplicate_sort's job."""
        nlp = self._nlp(
            [_make_token("manger", "VERB"), _make_token("manger", "VERB")]
        )
        with patch("lexikon.lemmatizer.spacy.load", return_value=nlp):
            result = extract_lemma_entries("manger manger")
        assert len(result) == 2


class TestDeduplicateSort:
    def test_deduplicates_by_lemma(self):
        entries = [
            LemmaEntry(lemma="manger", pos="VERB"),
            LemmaEntry(lemma="manger", pos="NOUN"),
            LemmaEntry(lemma="pain", pos="NOUN"),
        ]
        result = deduplicate_sort(entries)
        assert [e.lemma for e in result].count("manger") == 1

    def test_sorts_alphabetically(self):
        entries = [
            LemmaEntry(lemma="pain", pos="NOUN"),
            LemmaEntry(lemma="manger", pos="VERB"),
            LemmaEntry(lemma="eau", pos="NOUN"),
        ]
        result = deduplicate_sort(entries)
        assert [e.lemma for e in result] == ["eau", "manger", "pain"]

    def test_keeps_first_pos_on_duplicate(self):
        entries = [
            LemmaEntry(lemma="manger", pos="VERB"),
            LemmaEntry(lemma="manger", pos="NOUN"),
        ]
        result = deduplicate_sort(entries)
        assert result[0].pos == "VERB"

    def test_empty_input(self):
        assert deduplicate_sort([]) == []

    def test_min_frequency_drops_rare_lemmas(self):
        entries = [
            LemmaEntry(lemma="manger", pos="VERB"),
            LemmaEntry(lemma="manger", pos="VERB"),
            LemmaEntry(lemma="rare", pos="NOUN"),
        ]
        result = deduplicate_sort(entries, min_frequency=2)
        lemmas = [e.lemma for e in result]
        assert "manger" in lemmas
        assert "rare" not in lemmas

    def test_min_frequency_default_keeps_all(self):
        entries = [LemmaEntry(lemma="rare", pos="NOUN")]
        result = deduplicate_sort(entries)
        assert result[0].lemma == "rare"

    def test_gender_preserved_through_deduplication(self):
        entries = [
            LemmaEntry(lemma="professeur", pos="NOUN", gender="Masc"),
            LemmaEntry(lemma="professeur", pos="NOUN", gender="Masc"),
        ]
        result = deduplicate_sort(entries)
        assert result[0].gender == "Masc"
