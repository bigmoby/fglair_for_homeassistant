"""Test config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
import pytest

from custom_components.fglair_heatpump_controller.config_flow import (
    DATA_SCHEMA,
    FGLairIntegrationFlowHandler,
)
from custom_components.fglair_heatpump_controller.const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
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


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_step_user_no_input() -> None:
    """Test async_step_user with no user input."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    result = await handler.async_step_user(user_input=None)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "data_schema" in result


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_step_user_with_input() -> None:
    """Test async_step_user with user input."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    user_input = {
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
        CONF_REGION: "eu",
        CONF_TOKENPATH: "/test/path",
        CONF_TEMPERATURE_OFFSET: 1.0,
    }

    with patch.object(
        handler, "_create_client", return_value={"type": "create_entry"}
    ) as mock_create_client:
        await handler.async_step_user(user_input=user_input)

        mock_create_client.assert_called_once_with(
            username="test_user",
            password="test_pass",
            region="eu",
            tokenpath="/test/path",
            temperature_offset=1.0,
        )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_success() -> None:
    """Test _create_client success."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    mock_client = AsyncMock()
    mock_client.async_authenticate.return_value = "test_token"

    with (
        patch(
            "custom_components.fglair_heatpump_controller.config_flow.FGLairApiClient",
            return_value=mock_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.config_flow."
            "async_get_clientsession",
            return_value=MagicMock(),
        ),
        patch.object(
            handler, "_create_entry", return_value={"type": "create_entry"}
        ) as mock_create_entry,
    ):
        await handler._create_client(
            username="test_user",
            password="test_pass",
            region="eu",
            tokenpath="/test/path",
            temperature_offset=1.0,
        )

        mock_create_entry.assert_called_once_with(
            "test_user",
            "test_pass",
            "eu",
            "/test/path",
            1.0,
            "test_token",
        )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_timeout_error() -> None:
    """Test _create_client with timeout error."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    mock_client = AsyncMock()
    mock_client.async_authenticate.side_effect = TimeoutError("Timeout")

    with (
        patch(
            "custom_components.fglair_heatpump_controller.config_flow.FGLairApiClient",
            return_value=mock_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.config_flow."
            "async_get_clientsession",
            return_value=MagicMock(),
        ),
    ):
        result = await handler._create_client(
            username="test_user",
            password="test_pass",
            region="eu",
            tokenpath="/test/path",
            temperature_offset=1.0,
        )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "cannot_connect"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_connection_error() -> None:
    """Test _create_client with connection error."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    mock_client = AsyncMock()
    mock_client.async_authenticate.side_effect = ConnectionError("Connection failed")

    # ConnectionError is not handled in the current code, so it will raise
    with (
        pytest.raises(ConnectionError, match="Connection failed"),
        patch(
            "custom_components.fglair_heatpump_controller.config_flow.FGLairApiClient",
            return_value=mock_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.config_flow."
            "async_get_clientsession",
            return_value=MagicMock(),
        ),
    ):
        await handler._create_client(
            username="test_user",
            password="test_pass",
            region="eu",
            tokenpath="/test/path",
            temperature_offset=1.0,
        )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_blank_password() -> None:
    """Test _create_client with blank password."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    with pytest.raises(ValueError, match="Invalid internal state"):
        await handler._create_client(
            username="test_user",
            password="",  # Blank password
            region="eu",
            tokenpath="/test/path",
            temperature_offset=1.0,
        )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_blank_region() -> None:
    """Test _create_client with blank region."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    with pytest.raises(ValueError, match="Invalid internal state"):
        await handler._create_client(
            username="test_user",
            password="test_pass",
            region="",  # Blank region
            tokenpath="/test/path",
            temperature_offset=1.0,
        )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_entry_success() -> None:
    """Test _create_entry success."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    with patch.object(
        handler, "async_set_unique_id", return_value="unique_id"
    ) as mock_set_unique_id:
        result = await handler._create_entry(
            username="test_user",
            password="test_pass",
            region="eu",
            tokenpath="/test/path",
            temperature_offset=1.0,
            acquired_token="test_token",
        )

        mock_set_unique_id.assert_called_once_with("test_user")
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "test_user"
        assert result["data"][CONF_USERNAME] == "test_user"
        assert result["data"][CONF_PASSWORD] == "test_pass"
        assert result["data"][CONF_REGION] == "eu"
        assert result["data"][CONF_TOKENPATH] == "/test/path"
        assert result["data"][CONF_TEMPERATURE_OFFSET] == 1.0


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_entry_unique_id_configured() -> None:
    """Test _create_entry with already configured unique ID."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    with (
        patch.object(handler, "async_set_unique_id", return_value="unique_id"),
        patch.object(
            handler,
            "_abort_if_unique_id_configured",
            side_effect=Exception("Already configured"),
        ),
        pytest.raises(Exception, match="Already configured"),
    ):
        await handler._create_entry(
            username="test_user",
            password="test_pass",
            region="eu",
            tokenpath="/test/path",
            temperature_offset=1.0,
            acquired_token="test_token",
        )


def test_data_schema_structure() -> None:
    """Test DATA_SCHEMA structure."""
    assert CONF_USERNAME in DATA_SCHEMA.schema
    assert CONF_PASSWORD in DATA_SCHEMA.schema
    assert CONF_REGION in DATA_SCHEMA.schema
    assert CONF_TOKENPATH in DATA_SCHEMA.schema
    assert CONF_TEMPERATURE_OFFSET in DATA_SCHEMA.schema


def test_data_schema_defaults() -> None:
    """Test DATA_SCHEMA default values."""
    # Test that the schema has the expected structure
    assert CONF_USERNAME in DATA_SCHEMA.schema
    assert CONF_PASSWORD in DATA_SCHEMA.schema
    assert CONF_REGION in DATA_SCHEMA.schema
    assert CONF_TOKENPATH in DATA_SCHEMA.schema
    assert CONF_TEMPERATURE_OFFSET in DATA_SCHEMA.schema

    # Test that we can create a schema with defaults
    test_data = {
        CONF_USERNAME: "",
        CONF_PASSWORD: "",
        CONF_REGION: "eu",
        CONF_TOKENPATH: DEFAULT_TOKEN_PATH,
        CONF_TEMPERATURE_OFFSET: DEFAULT_TEMPERATURE_OFFSET,
    }

    # This should not raise an exception
    validated_data = DATA_SCHEMA(test_data)
    assert validated_data[CONF_USERNAME] == ""
    assert validated_data[CONF_PASSWORD] == ""
    assert validated_data[CONF_REGION] == "eu"
    assert validated_data[CONF_TOKENPATH] == DEFAULT_TOKEN_PATH
    assert validated_data[CONF_TEMPERATURE_OFFSET] == DEFAULT_TEMPERATURE_OFFSET


def test_handler_class_properties() -> None:
    """Test handler class properties."""
    handler = FGLairIntegrationFlowHandler()

    assert handler.VERSION == 1
    assert handler.hass is None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_with_different_regions() -> None:
    """Test _create_client with different regions."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    # Only test regions that are actually supported by FGLair
    regions = ["eu", "us"]

    for region in regions:
        mock_client = AsyncMock()
        mock_client.async_authenticate.return_value = f"token_{region}"

        with (
            patch(
                "custom_components.fglair_heatpump_controller.config_flow."
                "FGLairApiClient",
                return_value=mock_client,
            ),
            patch(
                "custom_components.fglair_heatpump_controller.config_flow."
                "async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch.object(
                handler, "_create_entry", return_value={"type": "create_entry"}
            ) as mock_create_entry,
        ):
            await handler._create_client(
                username=f"user_{region}",
                password="test_pass",
                region=region,
                tokenpath="/test/path",
                temperature_offset=1.0,
            )

            mock_create_entry.assert_called_once_with(
                f"user_{region}",
                "test_pass",
                region,
                "/test/path",
                1.0,
                f"token_{region}",
            )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_with_different_temperature_offsets() -> None:
    """Test _create_client with different temperature offsets."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    offsets = [-2.0, -1.0, 0.0, 1.0, 2.0]

    for offset in offsets:
        mock_client = AsyncMock()
        mock_client.async_authenticate.return_value = f"token_{offset}"

        with (
            patch(
                "custom_components.fglair_heatpump_controller.config_flow."
                "FGLairApiClient",
                return_value=mock_client,
            ),
            patch(
                "custom_components.fglair_heatpump_controller.config_flow."
                "async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch.object(
                handler, "_create_entry", return_value={"type": "create_entry"}
            ) as mock_create_entry,
        ):
            await handler._create_client(
                username="test_user",
                password="test_pass",
                region="eu",
                tokenpath="/test/path",
                temperature_offset=offset,
            )

            mock_create_entry.assert_called_once_with(
                "test_user",
                "test_pass",
                "eu",
                "/test/path",
                offset,
                f"token_{offset}",
            )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_client_with_special_characters() -> None:
    """Test _create_client with special characters in inputs."""
    handler = FGLairIntegrationFlowHandler()
    handler.hass = MagicMock(spec=HomeAssistant)

    special_inputs = {
        "username": "user@domain.com",
        "password": "pass!@#$%",
        "region": "eu",
        "tokenpath": "/path/with spaces",
    }

    mock_client = AsyncMock()
    mock_client.async_authenticate.return_value = "special_token"

    with (
        patch(
            "custom_components.fglair_heatpump_controller.config_flow.FGLairApiClient",
            return_value=mock_client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.config_flow."
            "async_get_clientsession",
            return_value=MagicMock(),
        ),
        patch.object(
            handler, "_create_entry", return_value={"type": "create_entry"}
        ) as mock_create_entry,
    ):
        await handler._create_client(
            username=special_inputs["username"],
            password=special_inputs["password"],
            region=special_inputs["region"],
            tokenpath=special_inputs["tokenpath"],
            temperature_offset=1.0,
        )

        mock_create_entry.assert_called_once_with(
            special_inputs["username"],
            special_inputs["password"],
            special_inputs["region"],
            special_inputs["tokenpath"],
            1.0,
            "special_token",
        )
