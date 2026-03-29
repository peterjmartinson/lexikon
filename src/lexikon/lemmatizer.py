import spacy
from dataclasses import dataclass


LANGUAGE_MODEL_MAP: dict[str, str] = {
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "es": "es_core_news_sm",
}

# POS tags that carry little lexical value and should be excluded.
EXCLUDED_POS: frozenset[str] = frozenset(
    {"SPACE", "PUNCT", "SYM", "NUM", "X", "DET", "ADP", "SCONJ", "CCONJ", "AUX"}
)


@dataclass
class LemmaEntry:
    lemma: str
    pos: str


def extract_lemma_entries(text: str, lang: str = "fr") -> list[LemmaEntry]:
    """Return a LemmaEntry for every content word in *text*.

    Uses the spaCy model mapped to *lang*.  Stop words, non-alpha tokens,
    single-character lemmas, and tokens with excluded POS tags are filtered out.

    Args:
        text: Pre-cleaned source text.
        lang: BCP-47 language code (e.g. ``"fr"``).

    Raises:
        ValueError: If *lang* is not in :data:`LANGUAGE_MODEL_MAP`.
    """
    model_name = LANGUAGE_MODEL_MAP.get(lang)
    if model_name is None:
        raise ValueError(
            f"Unsupported language: {lang!r}. Supported: {sorted(LANGUAGE_MODEL_MAP)}"
        )
    nlp = spacy.load(model_name)
    doc = nlp(text)
    entries: list[LemmaEntry] = []
    for token in doc:
        if (
            token.is_alpha
            and not token.is_stop
            and token.pos_ not in EXCLUDED_POS
        ):
            lemma = token.lemma_.lower().strip()
            if len(lemma) > 1:
                entries.append(LemmaEntry(lemma=lemma, pos=token.pos_))
    return entries


def deduplicate_sort(entries: list[LemmaEntry]) -> list[LemmaEntry]:
    """Deduplicate by lemma (keeping first POS seen) and sort alphabetically."""
    seen: dict[str, str] = {}
    for entry in entries:
        if entry.lemma not in seen:
            seen[entry.lemma] = entry.pos
    return sorted(
        [LemmaEntry(lemma=lemma, pos=pos) for lemma, pos in seen.items()],
        key=lambda e: e.lemma,
    )
