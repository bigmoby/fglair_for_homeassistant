"""Test climate entity."""

from unittest.mock import MagicMock

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
)


def test_climate_entity() -> None:
    """Test that climate entity can be instantiated."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=None,
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._dsn == "test-dsn"
    assert climate._region == "eu"


def test_climate_constants() -> None:
    """Test climate entity constants."""
    assert DEFAULT_TOKEN_PATH is not None
    assert DEFAULT_TEMPERATURE_OFFSET is not None
