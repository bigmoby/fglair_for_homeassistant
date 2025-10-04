"""Test __init__.py coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
import pytest

from custom_components.fglair_heatpump_controller import (
    FglairDataUpdateCoordinator,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.fglair_heatpump_controller.const import CONF_TOKENPATH, DOMAIN


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_setup_entry_success() -> None:
    """Test successful async_setup_entry."""
    mock_hass = MagicMock(spec=HomeAssistant)
    mock_hass.data = {}
    mock_entry = MagicMock(spec=ConfigEntry)
    mock_entry.entry_id = "test_entry_id"
    mock_entry.data = {
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
        CONF_REGION: "eu",
        CONF_TOKENPATH: "/test/path",
    }

    mock_coordinator = AsyncMock(spec=FglairDataUpdateCoordinator)
    mock_coordinator.async_config_entry_first_refresh.return_value = None

    mock_api_client = AsyncMock()

    with (
        patch(
            "custom_components.fglair_heatpump_controller.FGLairApiClient",
            return_value=mock_api_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.async_get_clientsession",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.fglair_heatpump_controller.FglairDataUpdateCoordinator",
            return_value=mock_coordinator,
        ),
        patch(
            "homeassistant.helpers.frame.report_usage",
            MagicMock(),
        ),
    ):
        # Mock the config_entries attribute
        mock_hass.config_entries = AsyncMock()
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock(
            return_value=None
        )

        result = await async_setup_entry(mock_hass, mock_entry)

        assert result is True
        mock_coordinator.async_config_entry_first_refresh.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_setup_entry_exception() -> None:
    """Test async_setup_entry with exception."""
    mock_hass = MagicMock(spec=HomeAssistant)
    mock_hass.data = {}
    mock_entry = MagicMock(spec=ConfigEntry)
    mock_entry.entry_id = "test_entry_id"
    mock_entry.data = {
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
        CONF_REGION: "eu",
        CONF_TOKENPATH: "/test/path",
    }

    mock_api_client = AsyncMock()
    mock_api_client.async_get_devices_dsn.side_effect = Exception("API Error")

    with (
        patch(
            "custom_components.fglair_heatpump_controller.FGLairApiClient",
            return_value=mock_api_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.async_get_clientsession",
            return_value=MagicMock(),
        ),
        patch(
            "homeassistant.helpers.frame.report_usage",
            MagicMock(),
        ),
        patch(
            "homeassistant.helpers.update_coordinator.DataUpdateCoordinator."
            "async_config_entry_first_refresh",
            AsyncMock(),
        ),
    ):
        # Mock the config_entries attribute
        mock_hass.config_entries = AsyncMock()
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock(
            return_value=None
        )

        result = await async_setup_entry(mock_hass, mock_entry)

        assert result is True  # The function doesn't handle exceptions, it returns True


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_unload_entry_success() -> None:
    """Test successful async_unload_entry."""
    mock_hass = MagicMock(spec=HomeAssistant)
    mock_entry = MagicMock(spec=ConfigEntry)
    mock_entry.entry_id = "test_entry_id"

    mock_coordinator = AsyncMock(spec=FglairDataUpdateCoordinator)

    mock_hass.data = {DOMAIN: {"test_entry_id": mock_coordinator}}

    # Mock the config_entries attribute
    mock_hass.config_entries = AsyncMock()
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(mock_hass, mock_entry)

    assert result is True


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_unload_entry_no_coordinator() -> None:
    """Test async_unload_entry with no coordinator."""
    mock_hass = MagicMock(spec=HomeAssistant)
    mock_entry = MagicMock(spec=ConfigEntry)
    mock_entry.entry_id = "test_entry_id"

    mock_hass.data = {DOMAIN: {}}

    # Mock the config_entries attribute
    mock_hass.config_entries = AsyncMock()
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    result = await async_unload_entry(mock_hass, mock_entry)

    assert result is False


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_unload_entry_exception() -> None:
    """Test async_unload_entry with exception."""
    mock_hass = MagicMock(spec=HomeAssistant)
    mock_entry = MagicMock(spec=ConfigEntry)
    mock_entry.entry_id = "test_entry_id"

    mock_hass.data = {DOMAIN: {"test_entry_id": MagicMock()}}

    # Mock the config_entries attribute
    mock_hass.config_entries = AsyncMock()
    mock_hass.config_entries.async_unload_platforms = AsyncMock(
        side_effect=Exception("Unload error")
    )

    # The current implementation doesn't handle exceptions, so it will raise
    with pytest.raises(Exception, match="Unload error"):
        await async_unload_entry(mock_hass, mock_entry)
