"""Bilingual string catalog tests (D-35, PRES-05)."""

from __future__ import annotations

import pytest

from scenecutbatch.i18n import (
    SUPPORTED_LANGUAGES,
    current_language,
    detect_language,
    normalize_language,
    set_language,
    t,
)


@pytest.fixture
def fresh_i18n():
    """Reset module-level language to Spanish around each test to avoid state leakage."""
    set_language("es")
    yield
    set_language("es")


def test_normalize_language_english(fresh_i18n):
    assert normalize_language("en_US") == "en"
    assert normalize_language("en-GB") == "en"
    assert normalize_language("english") == "en"


def test_normalize_language_spanish_fallback(fresh_i18n):
    assert normalize_language(None) == "es"
    assert normalize_language("") == "es"
    assert normalize_language("es_MX") == "es"
    assert normalize_language("fr_FR") == "es"
    assert normalize_language("de") == "es"
    assert normalize_language("pt_BR") == "es"


def test_supported_languages(fresh_i18n):
    assert SUPPORTED_LANGUAGES == ("en", "es")


def test_default_language_is_spanish(fresh_i18n):
    assert current_language() == "es"


def test_set_language_unknown_falls_back_to_spanish(fresh_i18n):
    set_language("xx")
    assert current_language() == "es"


def test_set_language_supported(fresh_i18n):
    set_language("en")
    assert current_language() == "en"
    set_language("es")
    assert current_language() == "es"


def test_t_unknown_key_returns_key(fresh_i18n):
    assert t("missing.key") == "missing.key"


def test_t_interpolation(fresh_i18n):
    set_language("en")
    assert t("log.clip_start", index=1, total=5, clip="video.mp4") == "[1/5] video.mp4 started"
    set_language("es")
    assert t("log.clip_start", index=1, total=5, clip="video.mp4") == "[1/5] video.mp4 iniciado"


def test_catalog_has_en_and_es_for_every_key(fresh_i18n):
    from scenecutbatch.i18n import STRINGS

    for key, entry in STRINGS.items():
        assert "en" in entry, f"key {key!r} missing 'en'"
        assert "es" in entry, f"key {key!r} missing 'es'"
