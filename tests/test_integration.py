"""Test integration setup."""

from custom_components.fglair_heatpump_controller import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.fglair_heatpump_controller.const import DOMAIN


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
    from custom_components.fglair_heatpump_controller import FglairDataUpdateCoordinator

    assert FglairDataUpdateCoordinator is not None
