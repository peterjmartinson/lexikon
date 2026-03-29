# lexikon

Reads a Project Gutenberg text in a foreign language and builds a lexicon: one entry per root form (lemma) with its primary English translation and part of speech, sorted alphabetically.

**Output format** (one line per lemma):

```
abondance (noun) - abundance
absolument (adverb) - absolutely
voyager (verb) - to travel
```

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)
- A Google Cloud project with the [Cloud Translation API](https://cloud.google.com/translate/docs) enabled
- Application Default Credentials: `gcloud auth application-default login`

## Setup

```bash
uv sync
# download the spaCy model for your source language (French by default):
uv run python -m spacy download fr_core_news_sm
```

Set your Google Cloud project:

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
```

## Usage

```bash
uv run python -m lexikon --gutenberg-file VerneVoyage.txt
```

| Flag | Description | Default |
|---|---|---|
| `--gutenberg-file FILE` | Path to the Gutenberg text file **(required)** | — |
| `--language LANG` | Source language code (`fr`, `de`, `es`) | `fr` |
| `--output FILE` | Output file path | `lexikon_output.txt` |

## Development

Install with dev dependencies and run the test suite:

```bash
uv sync --group dev
uv run pytest
uv run pytest -v   # verbose
```

All tests use mocked spaCy and Google Cloud clients — no model downloads or credentials are needed to run them.
