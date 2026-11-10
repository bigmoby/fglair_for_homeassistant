"""Config flow for the FGLair platform."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiohttp import ClientError
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_TOKEN, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import probatio
from pyfujitsugeneral.client import FGLairApiClient
from pyfujitsugeneral.utils import isBlank

from .const import (
    CONF_ACTION_THRESHOLD,
    CONF_METERS,
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DEFAULT_ACTION_THRESHOLD,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

DATA_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_USERNAME, default=""): str,
        probatio.Required(CONF_PASSWORD, default=""): str,
        probatio.Required(CONF_REGION, default="eu"): str,
        probatio.Required(CONF_TOKENPATH, default=DEFAULT_TOKEN_PATH): str,
        probatio.Required(
            CONF_TEMPERATURE_OFFSET, default=DEFAULT_TEMPERATURE_OFFSET
        ): probatio.Coerce(float),
    }
)


class FGLairIntegrationFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Options: upstream meter per device."""
        return FGLairOptionsFlow()

    async def _create_entry(  # pylint: disable=R0913
        self,
        *,
        username: str,
        password: str,
        region: str,
        tokenpath: str,
        temperature_offset: float,
        acquired_token: str,
    ) -> ConfigFlowResult:
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
    ) -> ConfigFlowResult:
        """Create client."""
        if isBlank(password) or isBlank(region):
            raise ValueError(
                "Invalid internal state. Called without either password or region"
            )

        try:
            async with asyncio.timeout(10):
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
        except TimeoutError, ClientError, ConnectionError:
            return self.async_abort(reason="cannot_connect")

        return await self._create_entry(
            username=username,
            password=password,
            region=region,
            tokenpath=tokenpath,
            temperature_offset=temperature_offset,
            acquired_token=acquired_token,
        )

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
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


class FGLairOptionsFlow(OptionsFlow):
    """Upstream meter per device and power threshold.

    One optional field per device (energy counter in kWh/Wh or power sensor in W, e.g. a
    smart plug in front of the indoor unit). The field label is the device name.
    """

    def _devices(self) -> dict[str, str]:
        """Dsn -> device name (names known from the last poll, else the dsn)."""
        data = self.hass.data.get(DOMAIN, {})
        coordinator = data.get(self.config_entry.entry_id)
        names = {dsn: (v[0] or dsn) for dsn, v in data.get("properties", {}).items()}
        dsns = list(getattr(coordinator, "devices", None) or names)
        return {dsn: names.get(dsn, dsn) for dsn in dsns}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show and save the upstream meters."""
        devices = self._devices()
        # field key = device name (shown as label); unique even if two devices share a
        # name
        keys: dict[str, str] = {}
        for dsn, name in devices.items():
            key = name if name not in keys else f"{name} ({dsn})"
            keys[key] = dsn
        meters: dict[str, str] = dict(self.config_entry.options.get(CONF_METERS) or {})

        if user_input is not None:
            new_meters = {
                dsn: user_input[key] for key, dsn in keys.items() if user_input.get(key)
            }
            return self.async_create_entry(
                data={
                    **self.config_entry.options,
                    CONF_METERS: new_meters,
                    CONF_ACTION_THRESHOLD: float(user_input[CONF_ACTION_THRESHOLD]),
                }
            )

        meter_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="sensor", device_class=["energy", "power"]
            )
        )
        schema: dict[Any, Any] = {}
        for key, dsn in keys.items():
            if meters.get(dsn):
                schema[
                    probatio.Optional(key, description={"suggested_value": meters[dsn]})
                ] = meter_selector
            else:
                schema[probatio.Optional(key)] = meter_selector
        schema[
            probatio.Required(
                CONF_ACTION_THRESHOLD,
                default=float(
                    self.config_entry.options.get(
                        CONF_ACTION_THRESHOLD, DEFAULT_ACTION_THRESHOLD
                    )
                ),
            )
        ] = selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=2000,
                step=10,
                unit_of_measurement="W",
                mode=selector.NumberSelectorMode.BOX,
            )
        )
        return self.async_show_form(step_id="init", data_schema=probatio.Schema(schema))
