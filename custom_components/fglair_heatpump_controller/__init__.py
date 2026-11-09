"""Custom integration to integrate FGLair Home Assistant Integration
with Home Assistant.
"""

import asyncio
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pyfujitsugeneral.client import FGLairApiClient
from pyfujitsugeneral.exceptions import FGLairGeneralException

from .const import (
    CONF_TOKENPATH,
    DEFAULT_TIMEOUT,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    PLATFORMS,
    SCAN_INTERVAL,
    STARTUP_MESSAGE,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Establish connection with FGLair."""

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    region = entry.data.get(CONF_REGION)
    tokenpath = entry.data.get(CONF_TOKENPATH, DEFAULT_TOKEN_PATH)

    session = async_get_clientsession(hass)
    client = FGLairApiClient(username, password, region, tokenpath, session)
    _install_login_guard(client, str(username))

    # One client shared by the background poll and the climate platform. The stored
    # token (file tokenpath) is used first; a new login only happens when it is no
    # longer valid (the FGLair cloud answers many logins in a row with 401 and then
    # stays locked for minutes). If it fails, the integration reports "not ready" and
    # Home Assistant retries by itself with a growing interval.
    try:
        async with asyncio.timeout(DEFAULT_TIMEOUT):
            devices = await client.async_get_devices_dsn()
    except Exception as exception:
        raise ConfigEntryNotReady(
            f"FGLair cloud not reachable or login failed ({exception})"
        ) from exception

    coordinator = FglairDataUpdateCoordinator(hass, client=client)
    coordinator.devices = devices
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


_LOGIN_REUSE = 60  # seconds a fresh login is shared by all requests
_LOGIN_BACKOFF_MIN = 120
_LOGIN_BACKOFF_MAX = 1800


# State per account across reloads/retries of the integration (otherwise the waiting
# time would start over with every "not ready" retry)
_LOGIN_STATE: dict[str, dict[str, Any]] = {}


def _install_login_guard(client: FGLairApiClient, account: str) -> None:
    """Throttle the logins of the library.

    pyfujitsugeneral logs in again after EVERY failed request (also after a timeout),
    for several units at the same time. The FGLair cloud rejects such login waves with
    401. Therefore: only one login at a time; a login younger than one minute is shared;
    after a failed login there is no login at all for 2 min, then 4, 8 ... up to 30 min.
    """
    original = client.async_authenticate
    state = _LOGIN_STATE.setdefault(
        account, {"ok": 0.0, "fail": 0.0, "backoff": 0.0, "lock": asyncio.Lock()}
    )
    state["ok"] = 0.0  # new client: its token is not verified yet
    lock = state["lock"]

    async def guarded() -> str:
        async with lock:
            now = time.monotonic()
            token = getattr(client, "_ACCESS_TOKEN_STR", None)
            if token and now - state["ok"] < _LOGIN_REUSE:
                return str(token)
            if now - state["fail"] < state["backoff"]:
                raise FGLairGeneralException
            try:
                token = await original()
            except FGLairGeneralException:
                state["fail"] = time.monotonic()
                state["backoff"] = min(
                    _LOGIN_BACKOFF_MAX, max(_LOGIN_BACKOFF_MIN, state["backoff"] * 2)
                )
                _LOGGER.warning(
                    "FGLair login failed - next login attempt in %d min",
                    state["backoff"] // 60,
                )
                raise
            if state["backoff"]:
                _LOGGER.info("FGLair login successful again")
            state["ok"], state["backoff"] = time.monotonic(), 0.0
            return token

    client.async_authenticate = guarded


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload FGLair config."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class FglairDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: FGLairApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        self.devices: list[str] = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> None:
        """Fetch data from library FGLairApiClient."""
        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                await self.client.async_get_devices_dsn()
        except Exception as exception:
            _LOGGER.warning("Failed to update coordinator data: %s", exception)
            raise UpdateFailed from exception
