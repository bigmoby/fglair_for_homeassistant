"""Test climate simple properties."""

from unittest.mock import MagicMock, patch

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
)


def test_climate_basic_properties() -> None:
    """Test basic climate properties."""
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
            hass=MagicMock(),
            coordinator=mock_coordinator,
        )

        # Test basic properties exist
        assert hasattr(climate, "unique_id")
        assert hasattr(climate, "name")
        assert hasattr(climate, "should_poll")
        assert hasattr(climate, "temperature_unit")
        assert hasattr(climate, "min_temp")
        assert hasattr(climate, "max_temp")
        assert hasattr(climate, "target_temperature_step")


def test_climate_mode_lists() -> None:
    """Test climate mode lists."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    # Test mode lists exist and are lists
    hvac_modes = climate.hvac_modes
    assert isinstance(hvac_modes, list)
    assert len(hvac_modes) > 0

    fan_modes = climate.fan_modes
    assert isinstance(fan_modes, list)
    assert len(fan_modes) > 0

    preset_modes = climate.preset_modes
    assert isinstance(preset_modes, list)
    assert len(preset_modes) > 0


def test_climate_temperature_properties() -> None:
    """Test climate temperature properties."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    # Test temperature properties
    assert climate.temperature_unit == "°C"
    assert isinstance(climate.min_temp, int | float)
    assert isinstance(climate.max_temp, int | float)
    assert climate.min_temp < climate.max_temp
    assert isinstance(climate.target_temperature_step, float)
    assert climate.target_temperature_step > 0


def test_climate_should_poll() -> None:
    """Test climate should_poll property."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate.should_poll is True


def test_climate_supported_features() -> None:
    """Test climate supported features."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    supported_features = climate.supported_features
    assert isinstance(supported_features, int)
    assert supported_features > 0


def test_climate_entity_registry() -> None:
    """Test climate entity registry enabled default."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate.entity_registry_enabled_default is True


def test_climate_device_info_exists() -> None:
    """Test climate device info exists."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    device_info = climate.device_info
    # device_info might be None, just check it exists
    assert device_info is None or isinstance(device_info, dict)


def test_climate_swing_modes_exists() -> None:
    """Test climate swing modes exists."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    swing_modes = climate.swing_modes
    # swing_modes might be None if device doesn't support swing modes
    assert swing_modes is None or isinstance(swing_modes, list)


def test_climate_async_methods_exist() -> None:
    """Test climate async methods exist."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    # Test async methods exist
    async_methods = [
        "async_set_temperature",
        "async_set_hvac_mode",
        "async_set_fan_mode",
        "async_set_swing_mode",
        "async_set_preset_mode",
        "async_turn_on",
        "async_turn_off",
        "async_update",
    ]

    for method_name in async_methods:
        assert hasattr(climate, method_name)
        assert callable(getattr(climate, method_name))
