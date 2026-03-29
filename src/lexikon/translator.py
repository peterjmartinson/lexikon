import os

from google.cloud import translate_v3


def translate_batch(
    lemmas: list[str],
    source_lang: str = "fr",
    target_lang: str = "en",
    project_id: str | None = None,
) -> dict[str, str]:
    """Translate *lemmas* in a single batch request via Cloud Translation API v3.

    Args:
        lemmas: List of source-language words to translate.
        source_lang: BCP-47 source language code (e.g. ``"fr"``).
        target_lang: BCP-47 target language code (e.g. ``"en"``).
        project_id: Google Cloud project ID.  Falls back to the
            ``GOOGLE_CLOUD_PROJECT`` environment variable.

    Returns:
        Mapping of each input lemma to its primary English translation.

    Raises:
        ValueError: If no project ID is available.
    """
    if project_id is None:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    if not project_id:
        raise ValueError(
            "A Google Cloud project ID is required. "
            "Set the GOOGLE_CLOUD_PROJECT environment variable or pass project_id."
        )

    client = translate_v3.TranslationServiceClient()
    parent = f"projects/{project_id}/locations/global"

    BATCH_SIZE = 1024
    results: dict[str, str] = {}
    for offset in range(0, len(lemmas), BATCH_SIZE):
        chunk = lemmas[offset : offset + BATCH_SIZE]
        response = client.translate_text(
            parent=parent,
            contents=chunk,
            target_language_code=target_lang,
            source_language_code=source_lang,
        )
        for lemma, translation in zip(chunk, response.translations):
            results[lemma] = translation.translated_text
    return results
