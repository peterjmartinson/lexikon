# Clean redesign: root forms lexicon builder with CLI, noise-stripping, unit tests, clean src/lexikon/ structure 

To create a maintainable and testable pipeline for building a <foreign language>→English lexicon from a Gutenberg text, let's start fresh with a modular design and modern best practices. This issue tracks the minimum milestone as described:

## Goal
- **Input**: A Gutenberg text file in a foreign language
- **Output**: A text file listing the root forms (lemmas) of each word, together with their primary translation and part of speech.
- **Command-line usage**: `uv run python -m lexikon --gutenberg-file <filename>`
- All logic should live under `src/lexikon`.
- Tests written first (TDD), functions with single responsibility, Pythonic, clean.

## Steps (atomic, checkable)

### Scaffolding and Initial Setup
- [ ] 1. Set up project structure:
    - `src/lexikon/` for all source code
    - `tests/` for tests
    - Minimal module with CLI scaffold using `argparse` and `__main__` to accept `--gutenberg-file <filename>`
    - Add initial test file (e.g., `tests/test_basic.py`, can fail initially)

### Text Loading and Cleaning
- [ ] 2. Implement function to load and read a Gutenberg text file (as UTF-8).
- [ ] 3. Implement and test a function to remove legal disclaimers and Gutenberg license noise from text.
- [ ] 4. Implement and test a function to remove all punctuation and normalize whitespace (tokenize cleanly on words).
- [ ] 5. Implement and test a function to filter out atom words (single-letter, possibly language-specific stop words).

### Lemmatization and Extraction
- [ ] 6. Implement and test function (using spaCy, or fallback) to get the root form (lemma) of each word in the cleaned text. Ensure language model is configurable.
- [ ] 7. Implement and test a function to deduplicate and sort unique lemmas.
  
### Translation and POS Tagging
- [ ] 8. Implement and test translation of each lemma (batch-friendly). Start with a simple API or dummy stub (real API in follow-ups).
- [ ] 9. Implement and test part-of-speech tagging for each lemma (stub or use spaCy's POS).

### Output and CLI
- [ ] 10. Implement function to write results to a plain text file: `lemma, translation, part-of-speech`, one per line, sorted.
- [ ] 11. Wire up the CLI (`python -m lexikon --gutenberg-file ...`) to run entire pipeline.

### Testing & Linting
- [ ] 12. Ensure all functions have isolated, clean unit tests (written before or alongside implementation).
- [ ] 13. Add minimal and realistic input files and expected outputs for tests.
  
### Documentation
- [ ] 14. Add or update README with usage + development instructions.

---
- Initially focus only on getting correct root forms, translations, and POS for each word; all bells and whistles (multiple output formats, alternate APIs, etc) are for future issues.
- Leave translation key/API architecture simple (if needed, can use mocks or stubs for CI/test).
- All commits must pass the tests before merging.

Add checklists for each step as PRs are created to track atomic progress.