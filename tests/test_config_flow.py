"""Test config flow."""

from custom_components.fglair_heatpump_controller.config_flow import (
    FGLairIntegrationFlowHandler,
)


def test_config_flow_handler() -> None:
    """Test that config flow handler can be instantiated."""
    handler = FGLairIntegrationFlowHandler()
    assert handler is not None
    assert handler.hass is None


def test_config_flow_version() -> None:
    """Test config flow version."""
    handler = FGLairIntegrationFlowHandler()
    assert handler.VERSION == 1


def test_config_flow_step_user_method_exists() -> None:
    """Test that step_user method exists."""
    handler = FGLairIntegrationFlowHandler()
    assert hasattr(handler, "async_step_user")
    assert callable(handler.async_step_user)
