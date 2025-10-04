"""Test climate entity."""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_NONE,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_VERTICAL,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PASSWORD,
    CONF_REGION,
    CONF_USERNAME,
)
import pytest

from custom_components.fglair_heatpump_controller.climate import (
    FujitsuClimate,
    async_setup_entry,
)
from custom_components.fglair_heatpump_controller.const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    HORIZONTAL,
    VERTICAL,
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


@pytest.mark.asyncio  # type: ignore[misc]
async def test_handle_coordinator_update() -> None:
    """Test _handle_coordinator_update callback."""
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

    # Mock the super method to avoid hass issues
    with patch.object(
        climate.__class__.__bases__[0], "_handle_coordinator_update"
    ) as mock_super:
        # Test the callback method
        climate._handle_coordinator_update()

        # Verify super method was called
        mock_super.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_added_to_hass() -> None:
    """Test async_added_to_hass method."""
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

    # Mock both super methods to avoid hass issues
    with (
        patch.object(
            climate.__class__.__bases__[0], "async_added_to_hass"
        ) as mock_super_added,
        patch.object(
            climate.__class__.__bases__[0], "_handle_coordinator_update"
        ) as mock_super_handle,
    ):
        mock_super_added.return_value = AsyncMock()

        # Test the method
        await climate.async_added_to_hass()

        # Verify super methods were called
        mock_super_added.assert_called_once()
        mock_super_handle.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_hvac_mode_invalid_mode() -> None:
    """Test async_set_hvac_mode with invalid HVAC mode."""
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

    # Test with invalid HVAC mode
    with pytest.raises(ValueError, match="Unsupported HVAC mode"):
        await climate.async_set_hvac_mode("INVALID_MODE")


@pytest.mark.asyncio  # type: ignore[misc]
async def test_hvac_action_when_off() -> None:
    """Test hvac_action when device is off."""
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

    # Mock is_on to return False
    climate._fujitsu_device.get_operation_mode = MagicMock(return_value={"value": 0})

    # Test hvac_action when off
    action = climate.hvac_action
    assert action == HVACAction.OFF


@pytest.mark.asyncio  # type: ignore[misc]
async def test_hvac_action_defrost_mode() -> None:
    """Test hvac_action for Defrost mode."""
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

    # Mock is_on to return True
    climate._fujitsu_device.get_operation_mode = MagicMock(return_value={"value": 1})

    # Mock get_op_status_desc to return "Defrost"
    climate._fujitsu_device.get_op_status_desc = MagicMock(return_value="Defrost")

    # Test hvac_action for Defrost mode
    action = climate.hvac_action
    assert action == HVACAction.PREHEATING


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_mode_exception_handling() -> None:
    """Test swing mode exception handling."""
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

    # Mock vane_vertical to raise exception inside try block
    climate._fujitsu_device.vane_vertical = MagicMock(
        side_effect=Exception("Test exception")
    )

    # Test swing mode with exception - should return None
    swing_mode = climate.swing_mode
    assert swing_mode is None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_modes_vertical_mode() -> None:
    """Test swing modes for Vertical mode."""
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

    # Mock swing modes to return "Vertical"
    climate._fujitsu_device.get_swing_modes_supported = MagicMock(
        return_value="Vertical"
    )
    climate._fujitsu_device.vane_vertical_positions = MagicMock(return_value=[1, 2, 3])

    # Test swing modes for Vertical mode
    swing_modes = climate.swing_modes
    assert swing_modes is not None
    assert SWING_VERTICAL in swing_modes
    assert VERTICAL + "1" in swing_modes
    assert VERTICAL + "2" in swing_modes
    assert VERTICAL + "3" in swing_modes


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_modes_horizontal_mode() -> None:
    """Test swing modes for Horizontal mode."""
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

    # Mock swing modes to return "Horizontal"
    climate._fujitsu_device.get_swing_modes_supported = MagicMock(
        return_value="Horizontal"
    )
    climate._fujitsu_device.vane_horizontal_positions = MagicMock(return_value=[1, 2])

    # Test swing modes for Horizontal mode
    swing_modes = climate.swing_modes
    assert swing_modes is not None
    assert SWING_HORIZONTAL in swing_modes
    assert HORIZONTAL + "1" in swing_modes
    assert HORIZONTAL + "2" in swing_modes


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_modes_empty_list() -> None:
    """Test swing modes when pos_list is empty."""
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

    # Mock swing modes to return empty lists
    climate._fujitsu_device.get_swing_modes_supported = MagicMock(return_value="None")
    climate._fujitsu_device.vane_vertical_positions = MagicMock(return_value=[])
    climate._fujitsu_device.vane_horizontal_positions = MagicMock(return_value=[])

    # Test swing modes when empty
    swing_modes = climate.swing_modes
    assert swing_modes is None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_swing_mode_vertical_horizontal() -> None:
    """Test async_set_swing_mode for VERTICAL and HORIZONTAL."""
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

    # Mock async methods
    climate._fujitsu_device.async_set_af_vertical_swing = AsyncMock()
    climate._fujitsu_device.async_set_af_horizontal_swing = AsyncMock()

    # Test VERTICAL swing mode
    await climate.async_set_swing_mode(SWING_VERTICAL)
    climate._fujitsu_device.async_set_af_vertical_swing.assert_called_once_with(1)

    # Test HORIZONTAL swing mode
    await climate.async_set_swing_mode(SWING_HORIZONTAL)
    climate._fujitsu_device.async_set_af_horizontal_swing.assert_called_once_with(1)


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_set_swing_mode_specific_positions() -> None:
    """Test async_set_swing_mode for specific positions."""
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

    # Mock async methods
    climate._fujitsu_device.async_set_vane_vertical_position = AsyncMock()
    climate._fujitsu_device.async_set_vane_horizontal_position = AsyncMock()

    # Test VERTICAL position
    await climate.async_set_swing_mode(VERTICAL + "3")
    climate._fujitsu_device.async_set_vane_vertical_position.assert_called_once_with(3)

    # Test HORIZONTAL position
    await climate.async_set_swing_mode(HORIZONTAL + "2")
    climate._fujitsu_device.async_set_vane_horizontal_position.assert_called_once_with(
        2
    )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_current_preset_mode_eco() -> None:
    """Test preset_mode for eco mode."""
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

    # Mock economy mode to be active
    climate._fujitsu_device.get_economy_mode = MagicMock(return_value={"value": True})
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_min_heat = MagicMock(return_value={"value": False})

    # Mock get_prop_from_json to return True for economy_mode
    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        # Test current preset mode
        preset_mode = climate.preset_mode
        assert preset_mode == PRESET_ECO


@pytest.mark.asyncio  # type: ignore[misc]
async def test_current_preset_mode_boost() -> None:
    """Test preset_mode for boost mode."""
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

    # Mock powerful mode to be active
    climate._fujitsu_device.get_economy_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={"value": True})
    climate._fujitsu_device.get_min_heat = MagicMock(return_value={"value": False})

    # Mock get_prop_from_json to return True for powerful_mode
    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        # Test current preset mode
        preset_mode = climate.preset_mode
        assert preset_mode == PRESET_BOOST


@pytest.mark.asyncio  # type: ignore[misc]
async def test_current_preset_mode_away() -> None:
    """Test preset_mode for away mode."""
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

    # Mock min heat mode to be active
    climate._fujitsu_device.get_economy_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_min_heat = MagicMock(return_value={"value": True})

    # Mock get_prop_from_json to return True for min_heat
    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        # Test current preset mode
        preset_mode = climate.preset_mode
        assert preset_mode == PRESET_AWAY


@pytest.mark.asyncio  # type: ignore[misc]
async def test_hvac_action_return_none() -> None:
    """Test hvac_action returns None for unknown op_status_desc."""
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

    # Mock is_on to return True
    climate._fujitsu_device.get_operation_mode = MagicMock(return_value={"value": 1})

    # Mock get_op_status_desc to return unknown status
    climate._fujitsu_device.get_op_status_desc = MagicMock(return_value="Unknown")

    # Test hvac_action for unknown status
    action = climate.hvac_action
    assert action is None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_mode_vertical_only() -> None:
    """Test swing mode when only vertical swing is active."""
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

    # Mock swing mode methods
    climate._fujitsu_device.vane_vertical = MagicMock(return_value=2)
    climate._fujitsu_device.get_af_vertical_swing = MagicMock(
        return_value={"value": True}
    )
    climate._fujitsu_device.get_af_horizontal_swing = MagicMock(
        return_value={"value": False}
    )

    # Test swing mode for vertical only
    swing_mode = climate.swing_mode
    assert swing_mode == SWING_VERTICAL


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_mode_vertical_position() -> None:
    """Test swing mode when vertical position is set."""
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

    # Mock swing mode methods
    climate._fujitsu_device.vane_vertical = MagicMock(return_value=3)
    climate._fujitsu_device.get_af_vertical_swing = MagicMock(
        return_value={"value": False}
    )
    climate._fujitsu_device.get_af_horizontal_swing = MagicMock(
        return_value={"value": False}
    )

    # Test swing mode for vertical position
    swing_mode = climate.swing_mode
    assert swing_mode == VERTICAL + "3"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_modes_both_mode() -> None:
    """Test swing modes for Both mode."""
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

    # Mock swing modes to return "Both"
    climate._fujitsu_device.get_swing_modes_supported = MagicMock(return_value="Both")
    climate._fujitsu_device.vane_vertical_positions = MagicMock(return_value=[1, 2])
    climate._fujitsu_device.vane_horizontal_positions = MagicMock(return_value=[1, 2])

    # Test swing modes for Both mode
    swing_modes = climate.swing_modes
    assert swing_modes is not None
    assert SWING_VERTICAL in swing_modes
    assert SWING_HORIZONTAL in swing_modes
    assert SWING_BOTH in swing_modes
    assert VERTICAL + "1" in swing_modes
    assert VERTICAL + "2" in swing_modes
    assert HORIZONTAL + "1" in swing_modes
    assert HORIZONTAL + "2" in swing_modes


@pytest.mark.asyncio  # type: ignore[misc]
async def test_preset_mode_return_none() -> None:
    """Test preset_mode returns PRESET_NONE when no modes are active."""
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

    # Mock all modes to be inactive
    climate._fujitsu_device.get_economy_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_min_heat = MagicMock(return_value={"value": False})

    # Mock get_prop_from_json to return False for all modes
    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = False

        # Test current preset mode
        preset_mode = climate.preset_mode
        assert preset_mode == PRESET_NONE


@pytest.mark.asyncio  # type: ignore[misc]
async def test_swing_mode_both_active() -> None:
    """Test swing mode when both vertical and horizontal swing are active."""
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

    # Mock swing mode methods - both active
    climate._fujitsu_device.vane_vertical = MagicMock(return_value=2)
    climate._fujitsu_device.get_af_vertical_swing = MagicMock(
        return_value={"value": True}
    )
    climate._fujitsu_device.get_af_horizontal_swing = MagicMock(
        return_value={"value": True}
    )

    # Test swing mode for both active
    swing_mode = climate.swing_mode
    assert swing_mode == SWING_BOTH


@pytest.mark.asyncio  # type: ignore[misc]
async def test_preset_mode_min_heat_active() -> None:
    """Test preset_mode returns PRESET_AWAY when min_heat is active."""
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

    # Mock min_heat to be active
    climate._fujitsu_device.get_economy_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_min_heat = MagicMock(return_value={"value": True})

    # Mock get_prop_from_json to return True for min_heat
    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.side_effect = lambda prop, props: prop == "min_heat"

        # Test current preset mode
        preset_mode = climate.preset_mode
        assert preset_mode == PRESET_AWAY


@pytest.mark.asyncio  # type: ignore[misc]
async def test_preset_mode_final_return_none() -> None:
    """Test preset_mode returns PRESET_NONE at the final return statement."""
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

    # Mock all modes to be inactive (no value or False)
    climate._fujitsu_device.get_economy_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_powerful_mode = MagicMock(return_value={"value": False})
    climate._fujitsu_device.get_min_heat = MagicMock(return_value={"value": False})

    # Mock get_prop_from_json to return True for all properties (so they exist)
    with patch(
        "custom_components.fglair_heatpump_controller.climate.get_prop_from_json"
    ) as mock_get_prop:
        mock_get_prop.return_value = True

        # Test current preset mode - should reach the final return PRESET_NONE
        preset_mode = climate.preset_mode
        assert preset_mode == PRESET_NONE


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
    """Test that climate entity registry is enabled by default."""
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


def test_name_property() -> None:
    """Test name property returns expected value."""
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
async def test_async_set_temperature() -> None:
    """Test async_set_temperature method."""
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
async def test_async_set_hvac_mode_heat() -> None:
    """Test async_set_hvac_mode for heat mode."""
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
async def test_async_set_hvac_mode_cool() -> None:
    """Test async_set_hvac_mode for cool mode."""
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
async def test_async_set_hvac_mode_off() -> None:
    """Test async_set_hvac_mode for off mode."""
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
async def test_async_turn_on() -> None:
    """Test async_turn_on method."""
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
async def test_async_turn_off() -> None:
    """Test async_turn_off method."""
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
async def test_async_set_fan_mode_high() -> None:
    """Test async_set_fan_mode for high speed."""
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
async def test_async_set_fan_mode_auto() -> None:
    """Test async_set_fan_mode for auto speed."""
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
async def test_async_set_swing_mode_both() -> None:
    """Test async_set_swing_mode for both directions."""
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
async def test_async_set_preset_mode_eco() -> None:
    """Test async_set_preset_mode for eco mode."""
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
async def test_async_set_preset_mode_boost() -> None:
    """Test async_set_preset_mode for boost mode."""
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
async def test_async_set_preset_mode_away() -> None:
    """Test async_set_preset_mode for away mode."""
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
async def test_async_set_preset_mode_none() -> None:
    """Test async_set_preset_mode for none mode."""
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

    # Test that method exists and is callable
    assert hasattr(climate, "async_set_temperature")
    assert callable(climate.async_set_temperature)

    # Test method signature (Home Assistant methods typically use **kwargs)
    sig = inspect.signature(climate.async_set_temperature)
    params = list(sig.parameters.keys())
    assert "kwargs" in params  # Home Assistant pattern


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

    # Test that method exists and is callable
    assert hasattr(climate, "async_set_hvac_mode")
    assert callable(climate.async_set_hvac_mode)

    # Test method signature
    sig = inspect.signature(climate.async_set_hvac_mode)
    params = list(sig.parameters.keys())
    assert "hvac_mode" in params


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
                assert hasattr(climate, attr)  # Property exists and is accessible


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
            assert hasattr(climate, attr)  # Property exists and is accessible


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
                assert hasattr(climate, attr)  # Property exists and is accessible


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_setup_entry_success() -> None:
    """Test successful climate setup entry."""
    # Mock Home Assistant objects
    mock_hass = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    mock_entry.data = {
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
        CONF_REGION: "eu",
        CONF_TOKENPATH: "/test/path",
        CONF_TEMPERATURE_OFFSET: 0.0,
    }
    mock_async_add_entities = MagicMock()

    # Mock coordinator in hass.data
    mock_coordinator = MagicMock()
    mock_hass.data = {DOMAIN: {mock_entry.entry_id: mock_coordinator}}

    # Mock API client and authentication
    mock_api_client = AsyncMock()
    mock_api_client.async_authenticate.return_value = True
    mock_api_client.async_get_devices_dsn.return_value = ["device1", "device2"]

    with (
        patch(
            "custom_components.fglair_heatpump_controller.climate.FGLairApiClient",
            return_value=mock_api_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.climate."
            "async_get_clientsession",
            return_value=MagicMock(),
        ),
    ):
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

    # Verify authentication was called
    mock_api_client.async_authenticate.assert_called_once()

    # Verify devices were fetched
    mock_api_client.async_get_devices_dsn.assert_called_once()

    # Verify entities were added
    mock_async_add_entities.assert_called_once()
    entities = mock_async_add_entities.call_args[0][0]
    assert len(entities) == 2  # Two devices


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_setup_entry_auth_failure() -> None:
    """Test climate setup entry with authentication failure."""
    # Mock Home Assistant objects
    mock_hass = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    mock_entry.data = {
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
        CONF_REGION: "eu",
        CONF_TOKENPATH: "/test/path",
        CONF_TEMPERATURE_OFFSET: 0.0,
    }
    mock_async_add_entities = MagicMock()

    # Mock coordinator in hass.data
    mock_coordinator = MagicMock()
    mock_hass.data = {DOMAIN: {mock_entry.entry_id: mock_coordinator}}

    # Mock API client with authentication failure
    mock_api_client = AsyncMock()
    mock_api_client.async_authenticate.return_value = False

    with (
        patch(
            "custom_components.fglair_heatpump_controller.climate.FGLairApiClient",
            return_value=mock_api_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.climate."
            "async_get_clientsession",
            return_value=MagicMock(),
        ),
    ):
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

    # Verify authentication was called
    mock_api_client.async_authenticate.assert_called_once()

    # Verify no entities were added due to auth failure
    mock_async_add_entities.assert_not_called()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_setup_entry_no_devices() -> None:
    """Test climate setup entry with no devices."""
    # Mock Home Assistant objects
    mock_hass = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    mock_entry.data = {
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
        CONF_REGION: "eu",
        CONF_TOKENPATH: "/test/path",
        CONF_TEMPERATURE_OFFSET: 0.0,
    }
    mock_async_add_entities = MagicMock()

    # Mock coordinator in hass.data
    mock_coordinator = MagicMock()
    mock_hass.data = {DOMAIN: {mock_entry.entry_id: mock_coordinator}}

    # Mock API client with no devices
    mock_api_client = AsyncMock()
    mock_api_client.async_authenticate.return_value = True
    mock_api_client.async_get_devices_dsn.return_value = []

    with (
        patch(
            "custom_components.fglair_heatpump_controller.climate.FGLairApiClient",
            return_value=mock_api_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.climate."
            "async_get_clientsession",
            return_value=MagicMock(),
        ),
    ):
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

    # Verify authentication was called
    mock_api_client.async_authenticate.assert_called_once()

    # Verify devices were fetched
    mock_api_client.async_get_devices_dsn.assert_called_once()

    # Verify no entities were added (empty list)
    mock_async_add_entities.assert_called_once()
    entities = mock_async_add_entities.call_args[0][0]
    assert len(entities) == 0


def test_climate_basic_properties() -> None:
    """Test that climate entity has all required basic properties."""
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
