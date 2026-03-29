import os

from lexikon.lemmatizer import LemmaEntry
from lexikon.writer import POS_LABELS, write_lexicon

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestPosLabels:
    def test_contains_common_pos_tags(self):
        for tag in ("NOUN", "VERB", "ADJ", "ADV"):
            assert tag in POS_LABELS

    def test_all_labels_are_lowercase(self):
        for label in POS_LABELS.values():
            assert label == label.lower()


class TestWriteLexicon:
    def test_writes_correct_format(self, tmp_path):
        entries = [
            LemmaEntry(lemma="professeur", pos="NOUN"),
            LemmaEntry(lemma="voyager", pos="VERB"),
        ]
        translations = {"professeur": "professor", "voyager": "to travel"}
        output_file = tmp_path / "output.txt"
        write_lexicon(entries, translations, str(output_file))

        lines = output_file.read_text(encoding="utf-8").strip().splitlines()
        assert "professeur (noun) - professor" in lines
        assert "voyager (verb) - to travel" in lines

    def test_output_is_sorted_alphabetically(self, tmp_path):
        entries = [
            LemmaEntry(lemma="voyager", pos="VERB"),
            LemmaEntry(lemma="impatient", pos="ADJ"),
        ]
        translations = {"voyager": "to travel", "impatient": "impatient"}
        output_file = tmp_path / "output.txt"
        write_lexicon(entries, translations, str(output_file))

        lines = output_file.read_text(encoding="utf-8").strip().splitlines()
        assert lines[0].startswith("impatient")
        assert lines[1].startswith("voyager")

    def test_adj_mapped_to_adjective(self, tmp_path):
        entries = [LemmaEntry(lemma="impatient", pos="ADJ")]
        output_file = tmp_path / "output.txt"
        write_lexicon(entries, {"impatient": "impatient"}, str(output_file))
        assert "adjective" in output_file.read_text(encoding="utf-8")

    def test_missing_translation_writes_empty(self, tmp_path):
        entries = [LemmaEntry(lemma="inconnu", pos="NOUN")]
        output_file = tmp_path / "output.txt"
        write_lexicon(entries, {}, str(output_file))
        assert "inconnu (noun) - " in output_file.read_text(encoding="utf-8")

    def test_unknown_pos_falls_back_to_lowercase(self, tmp_path):
        entries = [LemmaEntry(lemma="mot", pos="WEIRD")]
        output_file = tmp_path / "output.txt"
        write_lexicon(entries, {"mot": "word"}, str(output_file))
        assert "mot (weird) - word" in output_file.read_text(encoding="utf-8")

    def test_matches_expected_fixture(self, tmp_path):
        entries = [
            LemmaEntry(lemma="impatient", pos="ADJ"),
            LemmaEntry(lemma="professeur", pos="NOUN"),
            LemmaEntry(lemma="voyager", pos="VERB"),
        ]
        translations = {
            "impatient": "impatient",
            "professeur": "professor",
            "voyager": "to travel",
        }
        output_file = tmp_path / "output.txt"
        write_lexicon(entries, translations, str(output_file))

        expected_path = os.path.join(FIXTURES_DIR, "expected_output.txt")
        expected = open(expected_path, encoding="utf-8").read().strip()
        actual = output_file.read_text(encoding="utf-8").strip()
        assert actual == expected
