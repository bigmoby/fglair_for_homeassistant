"""Test basic functionality."""


def test_import() -> None:
    """Test that we can import the integration."""
    from custom_components.fglair_heatpump_controller import async_setup_entry
    from custom_components.fglair_heatpump_controller.const import DOMAIN

    assert async_setup_entry is not None
    assert DOMAIN == "fglair_heatpump_controller"


def test_constants() -> None:
    """Test that constants are defined."""
    from custom_components.fglair_heatpump_controller.const import DOMAIN

    assert DOMAIN == "fglair_heatpump_controller"
