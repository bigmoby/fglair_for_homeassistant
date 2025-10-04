"""Test constants."""

from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    PLATFORMS,
    SCAN_INTERVAL,
    VERSION,
)


def test_domain() -> None:
    """Test domain constant."""
    assert DOMAIN == "fglair_heatpump_controller"


def test_platforms() -> None:
    """Test platforms constant."""
    assert isinstance(PLATFORMS, list)
    assert "climate" in PLATFORMS


def test_default_values() -> None:
    """Test default values."""
    assert DEFAULT_TOKEN_PATH is not None
    assert isinstance(DEFAULT_TEMPERATURE_OFFSET, float)
    assert SCAN_INTERVAL is not None
    assert VERSION is not None


def test_version_type() -> None:
    """Test version is string."""
    assert isinstance(VERSION, str)
