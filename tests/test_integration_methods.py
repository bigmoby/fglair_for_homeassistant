"""Test integration functionality."""

import inspect
import json
import os
from unittest.mock import MagicMock, patch

from custom_components.fglair_heatpump_controller import (
    FglairDataUpdateCoordinator,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.config_flow import (
    FGLairIntegrationFlowHandler,
)
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    PLATFORMS,
    SCAN_INTERVAL,
    VERSION,
)


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


def test_integration_imports() -> None:
    """Test integration imports."""
    # Test that all necessary imports work
    assert FglairDataUpdateCoordinator is not None
    assert async_setup_entry is not None
    assert async_unload_entry is not None


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
