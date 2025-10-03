"""Test FGLair integration config flow."""

from custom_components.fglair_heatpump_controller.const import DOMAIN
import pytest

from .const import TEST_PASSWORD, TEST_REGION, TEST_USERNAME


@pytest.mark.asyncio  # type: ignore[misc]
async def test_constants() -> None:
    """Test that constants are properly defined."""
    assert DOMAIN == "fglair_heatpump_controller"
    assert TEST_USERNAME == "test-username"
    assert TEST_PASSWORD == "test-password"
    assert TEST_REGION == "eu"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_config_flow_imports() -> None:
    """Test that config flow can be imported."""
    from custom_components.fglair_heatpump_controller.config_flow import ConfigFlow

    assert ConfigFlow is not None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_climate_imports() -> None:
    """Test that climate component can be imported."""
    from custom_components.fglair_heatpump_controller.climate import FujitsuClimate

    assert FujitsuClimate is not None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_init_imports() -> None:
    """Test that __init__ module can be imported."""
    from custom_components.fglair_heatpump_controller import (
        async_setup_entry,
        async_unload_entry,
    )

    assert async_setup_entry is not None
    assert async_unload_entry is not None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_const_imports() -> None:
    """Test that constants module can be imported."""
    from custom_components.fglair_heatpump_controller.const import (
        DOMAIN,
        MAX_TEMP,
        MIN_TEMP,
        PLATFORMS,
        SCAN_INTERVAL,
        VERSION,
    )

    assert DOMAIN == "fglair_heatpump_controller"
    assert VERSION is not None
    assert PLATFORMS is not None
    assert SCAN_INTERVAL is not None
    assert MIN_TEMP is not None
    assert MAX_TEMP is not None
