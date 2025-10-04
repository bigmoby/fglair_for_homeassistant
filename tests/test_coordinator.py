"""Test data coordinator."""

from unittest.mock import MagicMock, patch

from custom_components.fglair_heatpump_controller import FglairDataUpdateCoordinator


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
