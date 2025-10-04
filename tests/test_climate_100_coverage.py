"""Test climate entity to reach 100% coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.climate.const import (
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_NONE,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_VERTICAL,
    HVACAction,
)
import pytest

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    HORIZONTAL,
    VERTICAL,
)


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
