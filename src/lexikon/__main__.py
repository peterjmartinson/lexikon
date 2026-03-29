"""Entry point: ``python -m lexikon``."""
import argparse
import sys

from lexikon.cleaner import (
    filter_short_tokens,
    remove_punctuation_normalize,
    strip_gutenberg_noise,
)
from lexikon.lemmatizer import deduplicate_sort, extract_lemma_entries
from lexikon.loader import load_text
from lexikon.translator import translate_batch
from lexikon.writer import write_lexicon


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="lexikon",
        description=(
            "Build a foreign-language → English lexicon from a Project Gutenberg text file."
        ),
    )
    parser.add_argument(
        "--gutenberg-file",
        required=True,
        metavar="FILE",
        help="Path to the Gutenberg text file (UTF-8).",
    )
    parser.add_argument(
        "--language",
        default="fr",
        metavar="LANG",
        help="BCP-47 source language code (default: fr). Supported: fr, de, es.",
    )
    parser.add_argument(
        "--output",
        default="lexikon_output.txt",
        metavar="FILE",
        help="Output file path (default: lexikon_output.txt).",
    )
    args = parser.parse_args(argv)

    print(f"Loading {args.gutenberg_file!r}...")
    text = load_text(args.gutenberg_file)

    print("Stripping Gutenberg noise...")
    text = strip_gutenberg_noise(text)

    print("Cleaning and tokenizing...")
    text = remove_punctuation_normalize(text)
    tokens = filter_short_tokens(text.split())

    print("Lemmatizing with spaCy...")
    entries = extract_lemma_entries(" ".join(tokens), lang=args.language)
    entries = deduplicate_sort(entries, min_frequency=2)
    print(f"  → {len(entries)} unique lemmas found.")

    print("Translating (Google Cloud Translation API)...")
    lemmas = [e.lemma for e in entries]
    translations = translate_batch(lemmas, source_lang=args.language)

    print(f"Writing lexicon to {args.output!r}...")
    write_lexicon(entries, translations, args.output)
    print("Done.")


if __name__ == "__main__":
    main()
