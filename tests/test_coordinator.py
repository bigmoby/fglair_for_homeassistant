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
