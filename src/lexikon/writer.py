from lexikon.lemmatizer import LemmaEntry


# Maps spaCy uppercase POS tags to human-readable lowercase labels.
POS_LABELS: dict[str, str] = {
    "NOUN": "noun",
    "VERB": "verb",
    "ADJ": "adjective",
    "ADV": "adverb",
    "PROPN": "noun",
    "PRON": "pronoun",
    "INTJ": "interjection",
}


def write_lexicon(
    entries: list[LemmaEntry],
    translations: dict[str, str],
    output_path: str,
) -> None:
    """Write the lexicon to *output_path*, one entry per line, sorted.

    Output format::

        lemma (part-of-speech) - translation

    Args:
        entries: Lemma entries (lemma + POS from spaCy).
        translations: Mapping of lemma → primary English translation.
        output_path: Destination file path (written as UTF-8).
    """
    sorted_entries = sorted(entries, key=lambda e: e.lemma)
    lines = []
    for entry in sorted_entries:
        pos_label = POS_LABELS.get(entry.pos, entry.pos.lower())
        translation = translations.get(entry.lemma, "")
        lines.append(f"{entry.lemma} ({pos_label}) - {translation}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
