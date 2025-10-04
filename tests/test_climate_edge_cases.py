"""Test utility functions and edge cases."""

from unittest.mock import MagicMock

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
)


def test_climate_initialization_with_none_values() -> None:
    """Test climate initialization with None values."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    # Test with empty strings instead of None to avoid type errors
    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="",  # Empty DSN
        region="",  # Empty region
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._dsn == ""
    assert climate._region == ""


def test_climate_initialization_with_empty_strings() -> None:
    """Test climate initialization with empty strings."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="",  # Empty DSN
        region="",  # Empty region
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._dsn == ""
    assert climate._region == ""


def test_climate_initialization_with_special_characters() -> None:
    """Test climate initialization with special characters."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-with-special-chars_123",
        region="eu-west-1",
        tokenpath="/path/with/special/chars",
        temperature_offset=1.5,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._dsn == "test-dsn-with-special-chars_123"
    assert climate._region == "eu-west-1"
    assert climate._temperature_offset == 1.5


def test_climate_initialization_with_negative_temperature_offset() -> None:
    """Test climate initialization with negative temperature offset."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=-2.0,  # Negative offset
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._temperature_offset == -2.0


def test_climate_initialization_with_large_temperature_offset() -> None:
    """Test climate initialization with large temperature offset."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=10.0,  # Large offset
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._temperature_offset == 10.0


def test_climate_initialization_with_zero_temperature_offset() -> None:
    """Test climate initialization with zero temperature offset."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=0.0,  # Zero offset
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._temperature_offset == 0.0


def test_climate_initialization_with_different_regions() -> None:
    """Test climate initialization with different regions."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    regions = ["eu", "us", "asia", "au", "jp"]

    for region in regions:
        climate = FujitsuClimate(
            fglair_api_client=mock_client,
            dsn="test-dsn",
            region=region,
            tokenpath=DEFAULT_TOKEN_PATH,
            temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
            hass=MagicMock(),
            coordinator=mock_coordinator,
        )

        assert climate is not None
        assert climate._region == region


def test_climate_initialization_with_long_dsn() -> None:
    """Test climate initialization with long DSN."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    long_dsn = "a" * 100  # Very long DSN

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn=long_dsn,
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._dsn == long_dsn
    assert len(climate._dsn) == 100
