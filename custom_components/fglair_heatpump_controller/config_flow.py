"""Config flow for the FGLair platform."""

from __future__ import annotations

import asyncio
import logging

import voluptuous as vol
from aiohttp import ClientError
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_REGION,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pyfujitsugeneral.client import FGLairApiClient
from pyfujitsugeneral.utils import isBlank

from .const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME, default=""): str,
        vol.Required(CONF_PASSWORD, default=""): str,
        vol.Required(CONF_REGION, default="eu"): str,
        vol.Required(CONF_TOKENPATH, default=DEFAULT_TOKEN_PATH): str,
        vol.Required(
            CONF_TEMPERATURE_OFFSET, default=DEFAULT_TEMPERATURE_OFFSET
        ): vol.Coerce(float),
    }
)


class FGLairIntegrationFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg] # pylint: disable=C0301 # noqa: E501
    """Handle a config flow."""

    VERSION = 1

    async def _create_entry(  # pylint: disable=R0913
        self,
        username: str,
        password: str,
        region: str,
        tokenpath: str,
        temperature_offset: float,
        acquired_token: str,
    ) -> FlowResult:
        """Register new entry."""
        unique_id = await self.async_set_unique_id(username)
        _LOGGER.debug("Creating unique ID %s", unique_id)
        self._abort_if_unique_id_configured({CONF_USERNAME: username})
        entry = self.async_create_entry(
            title=username,
            data={
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
                CONF_REGION: region,
                CONF_TOKENPATH: tokenpath,
                CONF_TEMPERATURE_OFFSET: temperature_offset,
                CONF_TOKEN: acquired_token,
            },
        )
        return entry

    async def _create_client(  # pylint: disable=R0913
        self,
        username: str,
        password: str,
        region: str,
        tokenpath: str,
        temperature_offset: float,
    ) -> FlowResult:
        """Create client."""
        if isBlank(password) or isBlank(region):
            raise ValueError(
                "Invalid internal state. Called without either password or"
                " region"
            )

        try:
            async with timeout(10):
                _client = FGLairApiClient(
                    username,
                    password,
                    region,
                    tokenpath,
                    async_get_clientsession(self.hass),
                )
                _LOGGER.debug("Invoking authenticate for %s", username)
                acquired_token = await _client.async_authenticate()
                _LOGGER.debug("authentication token %s", acquired_token)
        except (asyncio.TimeoutError, ClientError):
            return self.async_abort(reason="cannot_connect")

        return await self._create_entry(
            username,
            password,
            region,
            tokenpath,
            temperature_offset,
            acquired_token,
        )

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:  # type: ignore[type-arg] # pylint: disable=C0301 # noqa: E501
        """User initiated config flow."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=DATA_SCHEMA,
            )
        username = user_input[CONF_USERNAME]
        return await self._create_client(
            username=username,
            password=user_input[CONF_PASSWORD],
            region=user_input[CONF_REGION],
            tokenpath=user_input[CONF_TOKENPATH],
            temperature_offset=user_input[CONF_TEMPERATURE_OFFSET],
        )
