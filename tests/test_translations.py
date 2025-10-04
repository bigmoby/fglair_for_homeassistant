"""Test translations."""

import json
import os

from custom_components.fglair_heatpump_controller.const import DOMAIN


def test_translations_exist() -> None:
    """Test that translation files exist."""
    translations_dir = f"custom_components/{DOMAIN}/translations"

    assert os.path.exists(translations_dir)
    assert os.path.exists(f"{translations_dir}/en.json")
    assert os.path.exists(f"{translations_dir}/it.json")


def test_english_translations() -> None:
    """Test English translations are valid JSON."""
    translations_file = f"custom_components/{DOMAIN}/translations/en.json"

    with open(translations_file, encoding="utf-8") as f:
        translations = json.load(f)

    assert isinstance(translations, dict)
    assert "config" in translations
    assert "step" in translations["config"]


def test_italian_translations() -> None:
    """Test Italian translations are valid JSON."""
    translations_file = f"custom_components/{DOMAIN}/translations/it.json"

    with open(translations_file, encoding="utf-8") as f:
        translations = json.load(f)

    assert isinstance(translations, dict)
    assert "config" in translations
    assert "step" in translations["config"]
