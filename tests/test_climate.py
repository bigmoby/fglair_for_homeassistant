"""Test climate entity."""

from unittest.mock import MagicMock, patch

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


def test_climate_unique_id() -> None:
    """Test climate entity unique ID."""
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

    # Test that unique_id exists and is a string
    assert hasattr(climate, "unique_id")
    assert isinstance(climate.unique_id, str)
    assert len(climate.unique_id) > 0


def test_climate_name() -> None:
    """Test climate entity name."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    with patch(
        "pyfujitsugeneral.splitAC.SplitAC.get_device_name"
    ) as mock_get_device_name:
        # Mock the device name response
        mock_get_device_name.return_value = {"value": "Test Device"}

        climate = FujitsuClimate(
            fglair_api_client=mock_client,
            dsn="test-dsn",
            region="eu",
            tokenpath=DEFAULT_TOKEN_PATH,
            temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
            hass=None,
            coordinator=mock_coordinator,
        )

        # Test that name exists and is a string
        assert hasattr(climate, "name")
        assert isinstance(climate.name, str)
        assert len(climate.name) > 0


def test_climate_should_poll() -> None:
    """Test climate entity should_poll property."""
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

    assert climate.should_poll is True


def test_climate_hvac_modes() -> None:
    """Test climate entity HVAC modes."""
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

    hvac_modes = climate.hvac_modes
    assert isinstance(hvac_modes, list)
    assert len(hvac_modes) > 0


def test_climate_fan_modes() -> None:
    """Test climate entity fan modes."""
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

    fan_modes = climate.fan_modes
    assert isinstance(fan_modes, list)
    assert len(fan_modes) > 0


def test_climate_swing_modes() -> None:
    """Test climate entity swing modes."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    # Mock the swing mode responses
    mock_client.get_af_vertical_num_dir.return_value = {"value": 3}
    mock_client.get_af_horizontal_num_dir.return_value = {"value": 3}

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=None,
        coordinator=mock_coordinator,
    )

    swing_modes = climate.swing_modes
    # swing_modes might be None if device doesn't support swing modes
    assert swing_modes is None or isinstance(swing_modes, list)


def test_climate_preset_modes() -> None:
    """Test climate entity preset modes."""
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

    preset_modes = climate.preset_modes
    assert isinstance(preset_modes, list)
    assert len(preset_modes) > 0


def test_climate_temperature_unit() -> None:
    """Test climate entity temperature unit."""
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

    assert climate.temperature_unit == "°C"


def test_climate_min_temp() -> None:
    """Test climate entity minimum temperature."""
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

    # Test that min_temp exists and is a number
    assert hasattr(climate, "min_temp")
    assert isinstance(climate.min_temp, int | float)
    assert climate.min_temp > 0


def test_climate_max_temp() -> None:
    """Test climate entity maximum temperature."""
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

    # Test that max_temp exists and is a number
    assert hasattr(climate, "max_temp")
    assert isinstance(climate.max_temp, int | float)
    assert climate.max_temp > climate.min_temp


def test_climate_target_temperature_step() -> None:
    """Test climate entity target temperature step."""
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

    assert isinstance(climate.target_temperature_step, float)
    assert climate.target_temperature_step > 0
