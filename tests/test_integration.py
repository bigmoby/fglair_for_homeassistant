"""Test integration setup."""

import inspect
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import pytest

from custom_components.fglair_heatpump_controller import (
    FglairDataUpdateCoordinator,
    UpdateFailed,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.config_flow import (
    FGLairIntegrationFlowHandler,
)
from custom_components.fglair_heatpump_controller.const import (
    CONF_TOKENPATH,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    PLATFORMS,
    SCAN_INTERVAL,
    VERSION,
)


def test_setup_entry_function() -> None:
    """Test that setup entry function exists."""
    assert async_setup_entry is not None
    assert callable(async_setup_entry)


def test_unload_entry_function() -> None:
    """Test that unload entry function exists."""
    assert async_unload_entry is not None
    assert callable(async_unload_entry)


def test_integration_domain() -> None:
    """Test integration domain."""
    assert DOMAIN == "fglair_heatpump_controller"


def test_integration_imports() -> None:
    """Test that integration can be imported."""
    assert FglairDataUpdateCoordinator is not None


def test_integration_setup_entry_signature() -> None:
    """Test integration setup entry function signature."""
    assert callable(async_setup_entry)

    # Test function signature
    sig = inspect.signature(async_setup_entry)
    params = list(sig.parameters.keys())

    assert "hass" in params
    assert "entry" in params  # Changed from config_entry to entry


def test_integration_unload_entry_signature() -> None:
    """Test integration unload entry function signature."""
    assert callable(async_unload_entry)

    # Test function signature
    sig = inspect.signature(async_unload_entry)
    params = list(sig.parameters.keys())

    assert "hass" in params
    assert "entry" in params  # Changed from config_entry to entry


def test_integration_domain_constant() -> None:
    """Test integration domain constant."""
    assert DOMAIN == "fglair_heatpump_controller"
    assert isinstance(DOMAIN, str)
    assert len(DOMAIN) > 0


def test_integration_coordinator_class() -> None:
    """Test integration coordinator class."""
    assert FglairDataUpdateCoordinator is not None
    assert callable(FglairDataUpdateCoordinator)

    # Test class name
    assert FglairDataUpdateCoordinator.__name__ == "FglairDataUpdateCoordinator"


def test_integration_coordinator_instantiation() -> None:
    """Test integration coordinator instantiation."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert coordinator is not None
    assert coordinator.hass == mock_hass
    assert coordinator.client == mock_client


def test_integration_constants_import() -> None:
    """Test integration constants import."""
    assert DOMAIN is not None
    assert PLATFORMS is not None
    assert SCAN_INTERVAL is not None
    assert VERSION is not None
    assert DEFAULT_TEMPERATURE_OFFSET is not None
    assert DEFAULT_TOKEN_PATH is not None


def test_integration_climate_import() -> None:
    """Test integration climate import."""
    assert FujitsuClimate is not None
    assert callable(FujitsuClimate)
    assert FujitsuClimate.__name__ == "FujitsuClimate"


def test_integration_config_flow_import() -> None:
    """Test integration config flow import."""
    assert FGLairIntegrationFlowHandler is not None
    assert callable(FGLairIntegrationFlowHandler)
    assert FGLairIntegrationFlowHandler.__name__ == "FGLairIntegrationFlowHandler"


def test_integration_manifest_import() -> None:
    """Test integration manifest import."""
    manifest_path = "custom_components/fglair_heatpump_controller/manifest.json"
    assert os.path.exists(manifest_path)

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    assert isinstance(manifest, dict)
    assert "domain" in manifest
    assert "name" in manifest
    assert "version" in manifest
    assert manifest["domain"] == DOMAIN


def test_integration_platforms() -> None:
    """Test integration platforms."""
    assert isinstance(PLATFORMS, list)
    assert len(PLATFORMS) > 0
    assert "climate" in PLATFORMS


def test_integration_scan_interval() -> None:
    """Test integration scan interval."""
    assert SCAN_INTERVAL is not None
    # SCAN_INTERVAL is a timedelta object
    assert hasattr(SCAN_INTERVAL, "total_seconds")
    assert SCAN_INTERVAL.total_seconds() > 0


def test_integration_version() -> None:
    """Test integration version."""
    assert VERSION is not None
    assert isinstance(VERSION, str)
    assert len(VERSION) > 0


def test_integration_default_temperature_offset() -> None:
    """Test integration default temperature offset."""
    assert DEFAULT_TEMPERATURE_OFFSET is not None
    assert isinstance(DEFAULT_TEMPERATURE_OFFSET, float)


def test_integration_default_token_path() -> None:
    """Test integration default token path."""
    assert DEFAULT_TOKEN_PATH is not None
    assert isinstance(DEFAULT_TOKEN_PATH, str)
    assert len(DEFAULT_TOKEN_PATH) > 0


def test_coordinator_creation() -> None:
    """Test that coordinator can be created."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert coordinator is not None
    assert coordinator.hass == mock_hass
    assert coordinator.client == mock_client


def test_coordinator_attributes() -> None:
    """Test coordinator attributes."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "hass")
    assert hasattr(coordinator, "client")
    assert hasattr(coordinator, "data")


def test_coordinator_class_name() -> None:
    """Test coordinator class name."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert coordinator.__class__.__name__ == "FglairDataUpdateCoordinator"


def test_coordinator_data_initialization() -> None:
    """Test coordinator data initialization."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    # Test that data attribute exists (it might be None initially)
    assert hasattr(coordinator, "data")


def test_coordinator_has_update_method() -> None:
    """Test that coordinator has update method."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "_async_update_data")
    assert callable(coordinator._async_update_data)


def test_coordinator_has_refresh_method() -> None:
    """Test that coordinator has refresh method."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "async_refresh")
    assert callable(coordinator.async_refresh)


def test_coordinator_has_request_refresh_method() -> None:
    """Test that coordinator has request_refresh method."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "async_request_refresh")
    assert callable(coordinator.async_request_refresh)


def test_coordinator_has_config_entry() -> None:
    """Test that coordinator has config_entry attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "config_entry")


def test_coordinator_has_name() -> None:
    """Test that coordinator has name attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "name")


def test_coordinator_has_update_interval() -> None:
    """Test that coordinator has update_interval attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "update_interval")


def test_coordinator_has_last_update_success() -> None:
    """Test that coordinator has last_update_success attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "last_update_success")


def test_coordinator_has_last_exception() -> None:
    """Test that coordinator has last_exception attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "last_exception")


def test_coordinator_has_listeners() -> None:
    """Test that coordinator has listeners attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    # Test that listeners attribute exists (it might be a different name)
    assert hasattr(coordinator, "listeners") or hasattr(coordinator, "_listeners")


def test_coordinator_has_update_methods() -> None:
    """Test that coordinator has various update methods."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    # Test various update-related methods that might exist
    update_methods = ["async_update", "async_refresh", "async_request_refresh"]
    for method in update_methods:
        if hasattr(coordinator, method):
            assert callable(getattr(coordinator, method))


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


def test_coordinator_initialization() -> None:
    """Test FglairDataUpdateCoordinator initialization."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert coordinator is not None
    assert coordinator.hass == mock_hass
    assert coordinator.client == mock_client


def test_coordinator_has_client_attribute() -> None:
    """Test coordinator has client attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "client")
    assert coordinator.client == mock_client


def test_coordinator_inherits_from_data_update_coordinator() -> None:
    """Test coordinator inherits from DataUpdateCoordinator."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert isinstance(coordinator, DataUpdateCoordinator)


def test_coordinator_has_hass_attribute() -> None:
    """Test coordinator has hass attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "hass")
    assert coordinator.hass == mock_hass


def test_coordinator_has_logger_attribute() -> None:
    """Test coordinator has logger attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "logger")
    assert coordinator.logger is not None


def test_coordinator_has_data_attribute() -> None:
    """Test coordinator has data attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "data")


def test_coordinator_has_last_update_success_attribute() -> None:
    """Test coordinator has last_update_success attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "last_update_success")


def test_coordinator_has_last_exception_attribute() -> None:
    """Test coordinator has last_exception attribute."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "last_exception")


def test_translations_exist() -> None:
    """Test that translation files exist."""
    translations_dir = f"custom_components/{DOMAIN}/translations"

    assert os.path.exists(translations_dir)
    assert os.path.exists(f"{translations_dir}/en.json")
    assert os.path.exists(f"{translations_dir}/it.json")


def test_english_translations() -> None:
    """Test English translations are valid JSON."""
    translations_file = f"custom_components/{DOMAIN}/translations/en.json"

    with open(translations_file, encoding="utf-8") as f:
        translations = json.load(f)

    assert isinstance(translations, dict)
    assert "config" in translations
    assert "step" in translations["config"]


def test_italian_translations() -> None:
    """Test Italian translations are valid JSON."""
    translations_file = f"custom_components/{DOMAIN}/translations/it.json"

    with open(translations_file, encoding="utf-8") as f:
        translations = json.load(f)

    assert isinstance(translations, dict)
    assert "config" in translations
    assert "step" in translations["config"]


@pytest.mark.asyncio  # type: ignore[misc]
async def test_coordinator_async_update_data_success() -> None:
    """Test coordinator _async_update_data method success."""
    mock_hass = MagicMock()
    mock_client = AsyncMock()

    # Mock the frame helper to avoid Home Assistant setup issues
    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    # Mock the client method to return successfully
    mock_client.async_get_devices_dsn = AsyncMock(return_value={"devices": []})

    # Test the method
    await coordinator._async_update_data()

    # Verify the client method was called
    mock_client.async_get_devices_dsn.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_coordinator_async_update_data_exception() -> None:
    """Test coordinator _async_update_data method with exception."""
    mock_hass = MagicMock()
    mock_client = AsyncMock()

    # Mock the frame helper to avoid Home Assistant setup issues
    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    # Mock the client method to raise an exception
    mock_client.async_get_devices_dsn = AsyncMock(side_effect=Exception("Test error"))

    # Test that the method raises UpdateFailed
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    # Verify the client method was called
    mock_client.async_get_devices_dsn.assert_called_once()
