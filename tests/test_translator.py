import os
import pytest
from unittest.mock import MagicMock, patch

from lexikon.translator import translate_batch


def _make_mock_client(word_to_translation: dict[str, str]) -> MagicMock:
    mock_translations = []
    for translated_text in word_to_translation.values():
        item = MagicMock()
        item.translated_text = translated_text
        mock_translations.append(item)
    mock_response = MagicMock()
    mock_response.translations = mock_translations
    mock_client = MagicMock()
    mock_client.translate_text.return_value = mock_response
    return mock_client


class TestTranslateBatch:
    def test_returns_lemma_to_translation_mapping(self):
        expected = {"professeur": "professor", "voyager": "to travel"}
        mock_client = _make_mock_client(expected)
        with patch(
            "lexikon.translator.translate_v3.TranslationServiceClient",
            return_value=mock_client,
        ):
            result = translate_batch(list(expected.keys()), project_id="test-project")
        assert result == expected

    def test_calls_translate_text_exactly_once(self):
        mock_client = _make_mock_client({"eau": "water"})
        with patch(
            "lexikon.translator.translate_v3.TranslationServiceClient",
            return_value=mock_client,
        ):
            translate_batch(["eau"], project_id="test-project")
        mock_client.translate_text.assert_called_once()

    def test_passes_source_and_target_language(self):
        mock_client = _make_mock_client({"Wasser": "water"})
        with patch(
            "lexikon.translator.translate_v3.TranslationServiceClient",
            return_value=mock_client,
        ):
            translate_batch(["Wasser"], source_lang="de", project_id="test-project")
        _, kwargs = mock_client.translate_text.call_args
        assert kwargs["source_language_code"] == "de"
        assert kwargs["target_language_code"] == "en"

    def test_raises_without_project_id(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
        with pytest.raises(ValueError, match="GOOGLE_CLOUD_PROJECT"):
            translate_batch(["eau"])

    def test_uses_env_var_project_id(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "env-project")
        item = MagicMock()
        item.translated_text = "water"
        mock_response = MagicMock()
        mock_response.translations = [item]
        mock_client = MagicMock()
        mock_client.translate_text.return_value = mock_response
        with patch(
            "lexikon.translator.translate_v3.TranslationServiceClient",
            return_value=mock_client,
        ):
            translate_batch(["eau"])
        _, kwargs = mock_client.translate_text.call_args
        assert "env-project" in kwargs["parent"]
