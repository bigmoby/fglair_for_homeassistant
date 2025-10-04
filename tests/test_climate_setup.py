"""Test climate setup functions."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
import pytest

from custom_components.fglair_heatpump_controller.climate import async_setup_entry
from custom_components.fglair_heatpump_controller.const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DOMAIN,
)


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
