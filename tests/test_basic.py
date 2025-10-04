"""Test basic functionality."""

from custom_components.fglair_heatpump_controller import async_setup_entry
from custom_components.fglair_heatpump_controller.const import DOMAIN


def test_import() -> None:
    """Test that we can import the integration."""
    assert async_setup_entry is not None
    assert DOMAIN == "fglair_heatpump_controller"


def test_constants() -> None:
    """Test that constants are defined."""
    assert DOMAIN == "fglair_heatpump_controller"
