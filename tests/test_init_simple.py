"""Test integration __init__.py simple."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.fglair_heatpump_controller import FglairDataUpdateCoordinator
from custom_components.fglair_heatpump_controller.const import DOMAIN


def test_coordinator_initialization() -> None:
    """Test FglairDataUpdateCoordinator initialization."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert coordinator is not None
    assert coordinator.hass == mock_hass
    assert coordinator.client == mock_client


def test_coordinator_class_name() -> None:
    """Test FglairDataUpdateCoordinator class name."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert coordinator.__class__.__name__ == "FglairDataUpdateCoordinator"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_coordinator_async_update_data_success() -> None:
    """Test coordinator _async_update_data success."""
    mock_hass = MagicMock()
    mock_client = AsyncMock()
    mock_client.async_get_devices_dsn.return_value = ["device1", "device2"]

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    await coordinator._async_update_data()

    # Verify client method was called
    mock_client.async_get_devices_dsn.assert_called_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_coordinator_async_update_data_failure() -> None:
    """Test coordinator _async_update_data failure."""
    mock_hass = MagicMock()
    mock_client = AsyncMock()
    mock_client.async_get_devices_dsn.side_effect = Exception("API Error")

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    # Should raise UpdateFailed
    with pytest.raises(Exception) as exc_info:
        await coordinator._async_update_data()

    # Check that it's wrapped in UpdateFailed
    assert "UpdateFailed" in str(type(exc_info.value))


@pytest.mark.asyncio  # type: ignore[misc]
async def test_coordinator_async_update_data_timeout() -> None:
    """Test coordinator _async_update_data with timeout."""
    mock_hass = MagicMock()
    mock_client = AsyncMock()
    mock_client.async_get_devices_dsn.side_effect = TimeoutError("Timeout")

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    # Should raise UpdateFailed
    with pytest.raises(Exception) as exc_info:
        await coordinator._async_update_data()

    # Check that it's wrapped in UpdateFailed
    assert "UpdateFailed" in str(type(exc_info.value))


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
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert isinstance(coordinator, DataUpdateCoordinator)


def test_coordinator_has_update_interval() -> None:
    """Test coordinator has update_interval."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "update_interval")
    assert coordinator.update_interval is not None


def test_coordinator_has_name() -> None:
    """Test coordinator has name."""
    mock_hass = MagicMock()
    mock_client = MagicMock()

    with patch("homeassistant.helpers.frame.report_usage", MagicMock()):
        coordinator = FglairDataUpdateCoordinator(hass=mock_hass, client=mock_client)

    assert hasattr(coordinator, "name")
    assert coordinator.name == DOMAIN


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
