"""Global fixtures for fglair_heatpump_controller integration."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
)
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests.const import TEST_PASSWORD, TEST_REGION, TEST_USERNAME

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture  # type: ignore[misc]
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.fglair_heatpump_controller.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture  # type: ignore[misc]
def mock_config_entry(request: pytest.FixtureRequest) -> MockConfigEntry:
    """Return a regular config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=TEST_USERNAME,
        data={
            CONF_USERNAME: TEST_USERNAME,
            CONF_PASSWORD: TEST_PASSWORD,
            CONF_REGION: TEST_REGION,
            "tokenpath": DEFAULT_TOKEN_PATH,
            "temperature_offset": DEFAULT_TEMPERATURE_OFFSET,
        },
    )


'''@pytest.fixture
def mock_ayla_api(mock_devices: list[AsyncMock]) -> Generator[AsyncMock]:
    """Override FGLairApiClient creation."""
    my_mock = create_autospec(FGLairApiClient)

    with (
        patch(
            "homeassistant.components.fujitsu_fglair.new_ayla_api", return_value=my_mock
        ),
        patch(
            "homeassistant.components.fujitsu_fglair.config_flow.new_ayla_api",
            return_value=my_mock,
        ),
    ):
        my_mock.async_get_devices.return_value = mock_devices
        yield my_mock'''
