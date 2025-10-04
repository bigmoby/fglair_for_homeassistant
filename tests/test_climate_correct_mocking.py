"""Test climate entity comprehensive coverage - correct mocking."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_NONE,
    SWING_BOTH,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE
import pytest

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
)


def test_name_property_correct() -> None:
    """Test name property with correct mocking."""
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

    # Mock the device name response correctly
    climate._fujitsu_device.get_device_name = MagicMock(
        return_value={"value": "Test Device"}
    )

    name = climate.name
    assert name == "Test Device"


def test_is_aux_heat_on_property_true() -> None:
    """Test is_aux_heat_on property when true."""
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

    # Mock the powerful mode response - create a mock object with value attribute
    mock_response = MagicMock()
    mock_response.value = True
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value=mock_response)

    is_aux_heat = climate.is_aux_heat_on
    assert is_aux_heat is True


def test_is_aux_heat_on_property_false() -> None:
    """Test is_aux_heat_on property when false."""
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

    # Mock the powerful mode response
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={"value": False})

    is_aux_heat = climate.is_aux_heat_on
    assert is_aux_heat is False


def test_is_aux_heat_on_property_no_value() -> None:
    """Test is_aux_heat_on property when no value attribute."""
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

    # Mock the powerful mode response without value attribute
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={})

    is_aux_heat = climate.is_aux_heat_on
    assert is_aux_heat is False


def test_current_temperature_property() -> None:
    """Test current_temperature property."""
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

    # Set the internal temperature
    climate._current_temperature = 22.5

    temperature = climate.current_temperature
    assert temperature == 22.5


def test_current_temperature_property_none() -> None:
    """Test current_temperature property when None."""
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

    # Set the internal temperature to None
    climate._current_temperature = None

    temperature = climate.current_temperature
    assert temperature is None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_temperature_correct() -> None:
    """Test async_set_temperature with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_change_temperature = AsyncMock()

    # Test setting temperature
    kwargs = {ATTR_TEMPERATURE: 22.0}
    await climate.async_set_temperature(**kwargs)

    # Verify that the temperature was set
    climate._fujitsu_device.async_change_temperature.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_temperature_none() -> None:
    """Test async_set_temperature with None temperature."""
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

    # Mock the device methods
    climate._fujitsu_device.async_change_temperature = AsyncMock()

    # Test setting temperature with None
    kwargs = {ATTR_TEMPERATURE: None}
    await climate.async_set_temperature(**kwargs)

    # Verify that no temperature was set
    climate._fujitsu_device.async_change_temperature.assert_not_called()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_hvac_mode_heat_correct() -> None:
    """Test async_set_hvac_mode for heat with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_change_operation_mode = AsyncMock()

    await climate.async_set_hvac_mode(HVACMode.HEAT)

    # Verify that the HVAC mode was set
    climate._fujitsu_device.async_change_operation_mode.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_hvac_mode_cool_correct() -> None:
    """Test async_set_hvac_mode for cool with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_change_operation_mode = AsyncMock()

    await climate.async_set_hvac_mode(HVACMode.COOL)

    # Verify that the HVAC mode was set
    climate._fujitsu_device.async_change_operation_mode.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_hvac_mode_off_correct() -> None:
    """Test async_set_hvac_mode for off with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_turnOff = AsyncMock()

    await climate.async_set_hvac_mode(HVACMode.OFF)

    # Verify that the device was turned off
    climate._fujitsu_device.async_turnOff.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_turn_on_correct() -> None:
    """Test async_turn_on with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_turnOn = AsyncMock()

    await climate.async_turn_on()

    # Verify that the device was turned on
    climate._fujitsu_device.async_turnOn.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_turn_off_correct() -> None:
    """Test async_turn_off with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_turnOff = AsyncMock()

    await climate.async_turn_off()

    # Verify that the device was turned off
    climate._fujitsu_device.async_turnOff.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_fan_mode_high_correct() -> None:
    """Test async_set_fan_mode for high with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_changeFanSpeed = AsyncMock()

    await climate.async_set_fan_mode(FAN_HIGH)

    # Verify that the fan mode was set
    climate._fujitsu_device.async_changeFanSpeed.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_fan_mode_auto_correct() -> None:
    """Test async_set_fan_mode for auto with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_changeFanSpeed = AsyncMock()

    await climate.async_set_fan_mode(FAN_AUTO)

    # Verify that the fan mode was set
    climate._fujitsu_device.async_changeFanSpeed.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_swing_mode_both_correct() -> None:
    """Test async_set_swing_mode for both with correct mocking."""
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

    # Mock the device methods correctly
    climate._fujitsu_device.async_set_af_vertical_swing = AsyncMock()
    climate._fujitsu_device.async_set_af_horizontal_swing = AsyncMock()

    await climate.async_set_swing_mode(SWING_BOTH)

    # Verify that the swing modes were set
    climate._fujitsu_device.async_set_af_vertical_swing.assert_called_once()
    climate._fujitsu_device.async_set_af_horizontal_swing.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_preset_mode_eco_correct() -> None:
    """Test async_set_preset_mode for eco with correct mocking."""
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

    # Mock the device methods correctly based on pyfujitsugeneral structure
    climate._fujitsu_device.async_set_economy_mode = AsyncMock()
    climate._fujitsu_device.async_economy_mode_on = AsyncMock()
    climate._fujitsu_device.async_economy_mode_off = AsyncMock()
    climate._fujitsu_device.async_powerful_mode_off = AsyncMock()
    climate._fujitsu_device.async_min_heat_mode_off = AsyncMock()
    climate._fujitsu_device.get_economy_mode = MagicMock(
        return_value={"key": "economy_key"}
    )
    climate._fujitsu_device.get_powerful_mode = MagicMock(
        return_value={"key": "powerful_key"}
    )
    climate._fujitsu_device.get_min_heat = MagicMock(
        return_value={"key": "min_heat_key"}
    )
    climate._fujitsu_device.async_update_properties = AsyncMock(
        return_value={"economy_mode": True}
    )
    climate._fujitsu_device.get_device_name = MagicMock(
        return_value={"value": "Test Device"}
    )
    climate._fujitsu_device.get_refresh = MagicMock(
        return_value={"data_updated_at": "2024-01-01T00:00:00Z", "key": "refresh_key"}
    )
    climate._fujitsu_device.async_get_display_temperature_degree = AsyncMock(
        return_value=22.0
    )

    # Mock the internal client properly - this is the key!
    climate._fujitsu_device._client = AsyncMock()
    climate._fujitsu_device._client.async_set_device_property = AsyncMock()

    # Mock internal attributes that async_update needs
    climate._fujitsu_device._adjust_temperature = {"value": 22}
    climate._fujitsu_device.async_get_adjust_temperature_degree = AsyncMock(
        return_value=22.0
    )
    climate._fujitsu_device.get_fan_speed = MagicMock(
        return_value={"value": 2}
    )  # Medium speed
    climate._fujitsu_device.get_fan_speed_desc = MagicMock(return_value="Medium")
    climate._fujitsu_device.get_operation_mode = MagicMock(
        return_value={"value": 1}
    )  # Heat mode
    climate._fujitsu_device.get_operation_mode_desc = MagicMock(return_value="Heat")

    await climate.async_set_preset_mode(PRESET_ECO)

    # Verify that the preset mode was set
    climate._fujitsu_device.async_economy_mode_on.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_preset_mode_boost_correct() -> None:
    """Test async_set_preset_mode for boost with correct mocking."""
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

    # Mock the device methods correctly based on pyfujitsugeneral structure
    climate._fujitsu_device.async_set_powerful_mode = AsyncMock()
    climate._fujitsu_device.async_powerful_mode_on = AsyncMock()
    climate._fujitsu_device.async_powerful_mode_off = AsyncMock()
    climate._fujitsu_device.async_economy_mode_off = AsyncMock()
    climate._fujitsu_device.async_min_heat_mode_off = AsyncMock()
    climate._fujitsu_device.get_economy_mode = MagicMock(
        return_value={"key": "economy_key"}
    )
    climate._fujitsu_device.get_powerful_mode = MagicMock(
        return_value={"key": "powerful_key"}
    )
    climate._fujitsu_device.get_min_heat = MagicMock(
        return_value={"key": "min_heat_key"}
    )
    climate._fujitsu_device.async_update_properties = AsyncMock(
        return_value={"powerful_mode": True}
    )
    climate._fujitsu_device.get_device_name = MagicMock(
        return_value={"value": "Test Device"}
    )
    climate._fujitsu_device.get_refresh = MagicMock(
        return_value={"data_updated_at": "2024-01-01T00:00:00Z", "key": "refresh_key"}
    )
    climate._fujitsu_device.async_get_display_temperature_degree = AsyncMock(
        return_value=22.0
    )

    # Mock the internal client properly - this is the key!
    climate._fujitsu_device._client = AsyncMock()
    climate._fujitsu_device._client.async_set_device_property = AsyncMock()

    # Mock internal attributes that async_update needs
    climate._fujitsu_device._adjust_temperature = {"value": 22}
    climate._fujitsu_device.async_get_adjust_temperature_degree = AsyncMock(
        return_value=22.0
    )
    climate._fujitsu_device.get_fan_speed = MagicMock(
        return_value={"value": 2}
    )  # Medium speed
    climate._fujitsu_device.get_fan_speed_desc = MagicMock(return_value="Medium")
    climate._fujitsu_device.get_operation_mode = MagicMock(
        return_value={"value": 1}
    )  # Heat mode
    climate._fujitsu_device.get_operation_mode_desc = MagicMock(return_value="Heat")

    await climate.async_set_preset_mode(PRESET_BOOST)

    # Verify that the preset mode was set
    climate._fujitsu_device.async_powerful_mode_on.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_preset_mode_away_correct() -> None:
    """Test async_set_preset_mode for away with correct mocking."""
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

    # Mock the device methods correctly based on pyfujitsugeneral structure
    climate._fujitsu_device.async_set_min_heat = AsyncMock()
    climate._fujitsu_device.async_min_heat_mode_on = AsyncMock()
    climate._fujitsu_device.async_min_heat_mode_off = AsyncMock()
    climate._fujitsu_device.async_economy_mode_off = AsyncMock()
    climate._fujitsu_device.async_powerful_mode_off = AsyncMock()
    climate._fujitsu_device.get_economy_mode = MagicMock(
        return_value={"key": "economy_key"}
    )
    climate._fujitsu_device.get_powerful_mode = MagicMock(
        return_value={"key": "powerful_key"}
    )
    climate._fujitsu_device.get_min_heat = MagicMock(
        return_value={"key": "min_heat_key"}
    )
    climate._fujitsu_device.async_update_properties = AsyncMock(
        return_value={"min_heat": True}
    )
    climate._fujitsu_device.get_device_name = MagicMock(
        return_value={"value": "Test Device"}
    )
    climate._fujitsu_device.get_refresh = MagicMock(
        return_value={"data_updated_at": "2024-01-01T00:00:00Z", "key": "refresh_key"}
    )
    climate._fujitsu_device.async_get_display_temperature_degree = AsyncMock(
        return_value=22.0
    )

    # Mock the internal client properly - this is the key!
    climate._fujitsu_device._client = AsyncMock()
    climate._fujitsu_device._client.async_set_device_property = AsyncMock()

    # Mock internal attributes that async_update needs
    climate._fujitsu_device._adjust_temperature = {"value": 22}
    climate._fujitsu_device.async_get_adjust_temperature_degree = AsyncMock(
        return_value=22.0
    )
    climate._fujitsu_device.get_fan_speed = MagicMock(
        return_value={"value": 2}
    )  # Medium speed
    climate._fujitsu_device.get_fan_speed_desc = MagicMock(return_value="Medium")
    climate._fujitsu_device.get_operation_mode = MagicMock(
        return_value={"value": 1}
    )  # Heat mode
    climate._fujitsu_device.get_operation_mode_desc = MagicMock(return_value="Heat")

    await climate.async_set_preset_mode(PRESET_AWAY)

    # Verify that the preset mode was set
    climate._fujitsu_device.async_min_heat_mode_on.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_preset_mode_none_correct() -> None:
    """Test async_set_preset_mode for none with correct mocking."""
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

    # Mock the device methods correctly based on pyfujitsugeneral structure
    climate._fujitsu_device.async_set_economy_mode = AsyncMock()
    climate._fujitsu_device.async_set_powerful_mode = AsyncMock()
    climate._fujitsu_device.async_set_min_heat = AsyncMock()
    climate._fujitsu_device.async_economy_mode_off = AsyncMock()
    climate._fujitsu_device.async_powerful_mode_off = AsyncMock()
    climate._fujitsu_device.async_min_heat_mode_off = AsyncMock()
    climate._fujitsu_device.get_economy_mode = MagicMock(
        return_value={"key": "economy_key"}
    )
    climate._fujitsu_device.get_powerful_mode = MagicMock(
        return_value={"key": "powerful_key"}
    )
    climate._fujitsu_device.get_min_heat = MagicMock(
        return_value={"key": "min_heat_key"}
    )
    climate._fujitsu_device.async_update_properties = AsyncMock(
        return_value={"economy_mode": True, "powerful_mode": True, "min_heat": True}
    )
    climate._fujitsu_device.get_device_name = MagicMock(
        return_value={"value": "Test Device"}
    )
    climate._fujitsu_device.get_refresh = MagicMock(
        return_value={"data_updated_at": "2024-01-01T00:00:00Z", "key": "refresh_key"}
    )
    climate._fujitsu_device.async_get_display_temperature_degree = AsyncMock(
        return_value=22.0
    )

    # Mock the internal client properly - this is the key!
    climate._fujitsu_device._client = AsyncMock()
    climate._fujitsu_device._client.async_set_device_property = AsyncMock()

    # Mock internal attributes that async_update needs
    climate._fujitsu_device._adjust_temperature = {"value": 22}
    climate._fujitsu_device.async_get_adjust_temperature_degree = AsyncMock(
        return_value=22.0
    )
    climate._fujitsu_device.get_fan_speed = MagicMock(
        return_value={"value": 2}
    )  # Medium speed
    climate._fujitsu_device.get_fan_speed_desc = MagicMock(return_value="Medium")
    climate._fujitsu_device.get_operation_mode = MagicMock(
        return_value={"value": 1}
    )  # Heat mode
    climate._fujitsu_device.get_operation_mode_desc = MagicMock(return_value="Heat")

    await climate.async_set_preset_mode(PRESET_NONE)

    # Verify that all preset modes were turned off
    climate._fujitsu_device.async_economy_mode_off.assert_called_once()
    climate._fujitsu_device.async_powerful_mode_off.assert_called_once()
    climate._fujitsu_device.async_min_heat_mode_off.assert_called_once()


def test_get_supported_presets_economy_mode() -> None:
    """Test get_supported_presets with economy mode."""
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

    # Mock properties with economy mode
    climate._properties = {"economy_mode": True}  # type: ignore[assignment]

    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        presets = climate.get_supported_presets()
        assert PRESET_NONE in presets
        assert PRESET_ECO in presets


def test_get_supported_presets_powerful_mode() -> None:
    """Test get_supported_presets with powerful mode."""
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

    # Mock properties with powerful mode
    climate._properties = {"powerful_mode": True}  # type: ignore[assignment]

    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        presets = climate.get_supported_presets()
        assert PRESET_NONE in presets
        assert PRESET_BOOST in presets


def test_get_supported_presets_min_heat() -> None:
    """Test get_supported_presets with min heat."""
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

    # Mock properties with min heat
    climate._properties = {"min_heat": True}  # type: ignore[assignment]

    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        presets = climate.get_supported_presets()
        assert PRESET_NONE in presets
        assert PRESET_AWAY in presets


def test_get_supported_presets_multiple() -> None:
    """Test get_supported_presets with multiple modes."""
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

    # Mock properties with multiple modes
    climate._properties = {  # type: ignore[assignment]
        "economy_mode": True,
        "powerful_mode": True,
        "min_heat": True,
    }

    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        presets = climate.get_supported_presets()
        assert PRESET_NONE in presets
        assert PRESET_ECO in presets
        assert PRESET_BOOST in presets
        assert PRESET_AWAY in presets
        assert len(presets) == 4


def test_get_supported_presets_none() -> None:
    """Test get_supported_presets with no properties."""
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

    # Mock properties as None
    climate._properties = None

    presets = climate.get_supported_presets()
    assert PRESET_NONE in presets
    assert len(presets) == 1
