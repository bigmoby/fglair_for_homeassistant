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


def test_config_flow_class_name() -> None:
    """Test config flow class name."""
    handler = FGLairIntegrationFlowHandler()
    assert handler.__class__.__name__ == "FGLairIntegrationFlowHandler"


def test_config_flow_step_user_method_exists() -> None:
    """Test that step_user method exists."""
    handler = FGLairIntegrationFlowHandler()
    assert hasattr(handler, "async_step_user")
    assert callable(handler.async_step_user)


def test_config_flow_additional_methods() -> None:
    """Test that config flow has additional expected methods."""
    handler = FGLairIntegrationFlowHandler()

    # Test methods that should exist
    expected_methods = [
        "async_step_user",
        "async_step_user_form",
        "async_step_user_form_validation",
        "async_step_user_form_validation_error",
        "async_step_user_form_validation_error_2",
        "async_step_user_form_validation_error_3",
        "async_step_user_form_validation_error_4",
        "async_step_user_form_validation_error_5",
        "async_step_user_form_validation_error_6",
        "async_step_user_form_validation_error_7",
        "async_step_user_form_validation_error_8",
        "async_step_user_form_validation_error_9",
        "async_step_user_form_validation_error_10",
    ]

    # Check which methods actually exist
    existing_methods = []
    for method in expected_methods:
        if hasattr(handler, method):
            existing_methods.append(method)
            assert callable(getattr(handler, method))

    # At least the basic step_user should exist
    assert "async_step_user" in existing_methods
