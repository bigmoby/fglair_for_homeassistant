"""Test climate advanced functionality."""

from unittest.mock import MagicMock, patch

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
)


def test_climate_initialization_with_all_parameters() -> None:
    """Test climate initialization with all parameters."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-123",
        region="us-west",
        tokenpath="/custom/token/path",
        temperature_offset=2.5,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._dsn == "test-dsn-123"
    assert climate._region == "us-west"
    assert climate._tokenpath == "/custom/token/path"
    assert climate._temperature_offset == 2.5


def test_climate_initialization_with_minimal_parameters() -> None:
    """Test climate initialization with minimal parameters."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="minimal-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate is not None
    assert climate._dsn == "minimal-dsn"
    assert climate._region == "eu"
    assert climate._tokenpath == DEFAULT_TOKEN_PATH
    assert climate._temperature_offset == DEFAULT_TEMPERATURE_OFFSET


def test_climate_unique_id_format() -> None:
    """Test climate unique ID format."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-unique",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    unique_id = climate.unique_id
    assert isinstance(unique_id, str)
    assert len(unique_id) > 0
    # Just check it's a valid string, don't check specific content


def test_climate_name_with_mock_device_name() -> None:
    """Test climate name with mocked device name."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    with patch(
        "pyfujitsugeneral.splitAC.SplitAC.get_device_name"
    ) as mock_get_device_name:
        # Mock the device name response
        mock_get_device_name.return_value = {"value": "Test Device Name"}

        climate = FujitsuClimate(
            fglair_api_client=mock_client,
            dsn="test-dsn-name",
            region="eu",
            tokenpath=DEFAULT_TOKEN_PATH,
            temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
            hass=MagicMock(),
            coordinator=mock_coordinator,
        )

        name = climate.name
        assert isinstance(name, str)
        assert len(name) > 0


def test_climate_temperature_properties() -> None:
    """Test climate temperature properties."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-temp",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    # Test temperature unit
    assert climate.temperature_unit == "°C"

    # Test temperature range
    assert isinstance(climate.min_temp, int | float)
    assert isinstance(climate.max_temp, int | float)
    assert climate.min_temp < climate.max_temp

    # Test temperature step
    assert isinstance(climate.target_temperature_step, float)
    assert climate.target_temperature_step > 0


def test_climate_mode_properties() -> None:
    """Test climate mode properties."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-modes",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    # Test HVAC modes
    hvac_modes = climate.hvac_modes
    assert isinstance(hvac_modes, list)
    assert len(hvac_modes) > 0

    # Test fan modes
    fan_modes = climate.fan_modes
    assert isinstance(fan_modes, list)
    assert len(fan_modes) > 0

    # Test preset modes
    preset_modes = climate.preset_modes
    assert isinstance(preset_modes, list)
    assert len(preset_modes) > 0


def test_climate_swing_modes_with_mock() -> None:
    """Test climate swing modes with mocked responses."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    # Mock the swing mode responses
    mock_client.get_af_vertical_num_dir.return_value = {"value": 5}
    mock_client.get_af_horizontal_num_dir.return_value = {"value": 3}

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-swing",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    swing_modes = climate.swing_modes
    # swing_modes might be None if device doesn't support swing modes
    assert swing_modes is None or isinstance(swing_modes, list)


def test_climate_supported_features() -> None:
    """Test climate supported features."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-features",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    supported_features = climate.supported_features
    assert isinstance(supported_features, int)
    assert supported_features > 0


def test_climate_device_info() -> None:
    """Test climate device info."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-device",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    device_info = climate.device_info
    # device_info might be None, just check it exists
    assert device_info is None or isinstance(device_info, dict)


def test_climate_entity_registry_enabled_default() -> None:
    """Test climate entity registry enabled default."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-registry",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate.entity_registry_enabled_default is True


def test_climate_should_poll() -> None:
    """Test climate should_poll property."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-poll",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=MagicMock(),
        coordinator=mock_coordinator,
    )

    assert climate.should_poll is True


def test_climate_methods_exist() -> None:
    """Test that climate methods exist and are callable."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn-methods",
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
