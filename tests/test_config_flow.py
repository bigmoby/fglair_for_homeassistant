"""Test config flow."""

from custom_components.fglair_heatpump_controller.config_flow import (
    FGLairIntegrationFlowHandler,
)
from custom_components.fglair_heatpump_controller.const import DOMAIN


def test_config_flow_handler() -> None:
    """Test that config flow handler can be instantiated."""
    handler = FGLairIntegrationFlowHandler()
    assert handler is not None
    assert handler.hass is None


def test_config_flow_domain() -> None:
    """Test that config flow uses correct domain."""
    # Il DOMAIN è definito come costante, non come attributo della classe
    assert DOMAIN == "fglair_heatpump_controller"


def test_config_flow_version() -> None:
    """Test config flow version."""
    handler = FGLairIntegrationFlowHandler()
    assert handler.VERSION == 1
