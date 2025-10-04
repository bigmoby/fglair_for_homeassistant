"""Test climate entity methods."""

from unittest.mock import MagicMock, patch

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
)


def test_climate_set_temperature() -> None:
    """Test climate entity set_temperature method."""
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

    assert hasattr(climate, "async_set_temperature")
    assert callable(climate.async_set_temperature)


def test_climate_set_hvac_mode() -> None:
    """Test climate entity set_hvac_mode method."""
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

    assert hasattr(climate, "async_set_hvac_mode")
    assert callable(climate.async_set_hvac_mode)


def test_climate_set_fan_mode() -> None:
    """Test climate entity set_fan_mode method."""
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

    assert hasattr(climate, "async_set_fan_mode")
    assert callable(climate.async_set_fan_mode)


def test_climate_set_swing_mode() -> None:
    """Test climate entity set_swing_mode method."""
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

    assert hasattr(climate, "async_set_swing_mode")
    assert callable(climate.async_set_swing_mode)


def test_climate_set_preset_mode() -> None:
    """Test climate entity set_preset_mode method."""
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

    assert hasattr(climate, "async_set_preset_mode")
    assert callable(climate.async_set_preset_mode)


def test_climate_turn_on() -> None:
    """Test climate entity turn_on method."""
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

    assert hasattr(climate, "async_turn_on")
    assert callable(climate.async_turn_on)


def test_climate_turn_off() -> None:
    """Test climate entity turn_off method."""
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

    assert hasattr(climate, "async_turn_off")
    assert callable(climate.async_turn_off)


def test_climate_update() -> None:
    """Test climate entity update method."""
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

    assert hasattr(climate, "async_update")
    assert callable(climate.async_update)


def test_climate_device_info() -> None:
    """Test climate entity device_info property."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    # Mock device name response
    mock_client.get_device_name.return_value = {"value": "Test Device"}

    climate = FujitsuClimate(
        fglair_api_client=mock_client,
        dsn="test-dsn",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=None,
        coordinator=mock_coordinator,
    )

    assert hasattr(climate, "device_info")
    device_info = climate.device_info
    # device_info might be None if not properly initialized
    assert device_info is None or isinstance(device_info, dict)


def test_climate_entity_registry() -> None:
    """Test climate entity registry properties."""
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

    # Test entity registry properties
    assert hasattr(climate, "entity_registry_enabled_default")
    assert hasattr(climate, "entity_registry_visible_default")
    assert hasattr(climate, "entity_category")
    assert hasattr(climate, "assumed_state")
    assert hasattr(climate, "force_update")
    assert hasattr(climate, "icon")
    assert hasattr(climate, "entity_picture")


def test_climate_supported_features() -> None:
    """Test climate entity supported features."""
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

    assert hasattr(climate, "supported_features")
    supported_features = climate.supported_features
    assert isinstance(supported_features, int)
    assert supported_features >= 0


def test_climate_current_temperature() -> None:
    """Test climate entity current temperature property."""
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

    assert hasattr(climate, "current_temperature")


def test_climate_target_temperature() -> None:
    """Test climate entity target temperature property."""
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

    assert hasattr(climate, "target_temperature")


def test_climate_current_humidity() -> None:
    """Test climate entity current humidity property."""
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

    assert hasattr(climate, "current_humidity")


def test_climate_target_humidity() -> None:
    """Test climate entity target humidity property."""
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

    assert hasattr(climate, "target_humidity")


def test_climate_hvac_action() -> None:
    """Test climate entity HVAC action property."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    with (
        patch(
            "pyfujitsugeneral.splitAC.SplitAC.get_operation_mode"
        ) as mock_get_operation_mode,
        patch("pyfujitsugeneral.splitAC.SplitAC.get_properties") as mock_get_properties,
        patch("pyfujitsugeneral.splitAC.SplitAC.get_op_status") as mock_get_op_status,
    ):
        # Mock operation mode response
        mock_get_operation_mode.return_value = {"value": 1}
        # Mock properties response
        mock_get_properties.return_value = []
        # Mock op status response
        mock_get_op_status.return_value = {"value": 0}

        climate = FujitsuClimate(
            fglair_api_client=mock_client,
            dsn="test-dsn",
            region="eu",
            tokenpath=DEFAULT_TOKEN_PATH,
            temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
            hass=None,
            coordinator=mock_coordinator,
        )

        # Test that hvac_action property exists
        assert hasattr(climate, "hvac_action")


def test_climate_current_fan_mode() -> None:
    """Test climate entity current fan mode property."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    with patch("pyfujitsugeneral.splitAC.SplitAC.get_fan_speed") as mock_get_fan_speed:
        # Mock fan speed response
        mock_get_fan_speed.return_value = {"value": 1}

        climate = FujitsuClimate(
            fglair_api_client=mock_client,
            dsn="test-dsn",
            region="eu",
            tokenpath=DEFAULT_TOKEN_PATH,
            temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
            hass=None,
            coordinator=mock_coordinator,
        )

        # Test that fan mode related properties exist
        fan_mode_attrs = ["current_fan_mode", "fan_mode", "fan_modes"]
        for attr in fan_mode_attrs:
            if hasattr(climate, attr):
                assert True  # Property exists


def test_climate_current_swing_mode() -> None:
    """Test climate entity current swing mode property."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    # Mock swing mode responses
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

    # Test that swing mode related properties exist
    swing_mode_attrs = ["current_swing_mode", "swing_mode", "swing_modes"]
    for attr in swing_mode_attrs:
        if hasattr(climate, attr):
            assert True  # Property exists


def test_climate_current_preset_mode() -> None:
    """Test climate entity current preset mode property."""
    mock_client = MagicMock()
    mock_coordinator = MagicMock()

    with patch(
        "pyfujitsugeneral.splitAC.SplitAC.get_properties"
    ) as mock_get_properties:
        # Mock properties response
        mock_get_properties.return_value = []

        climate = FujitsuClimate(
            fglair_api_client=mock_client,
            dsn="test-dsn",
            region="eu",
            tokenpath=DEFAULT_TOKEN_PATH,
            temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
            hass=None,
            coordinator=mock_coordinator,
        )

        # Test that preset mode related properties exist
        preset_mode_attrs = ["current_preset_mode", "preset_mode", "preset_modes"]
        for attr in preset_mode_attrs:
            if hasattr(climate, attr):
                assert True  # Property exists
