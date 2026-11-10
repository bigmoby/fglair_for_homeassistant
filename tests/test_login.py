"""Shared FGLair client and login guard (throttling of the library's logins)."""

import asyncio
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
from pyfujitsugeneral.exceptions import FGLairGeneralException
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components import fglair_heatpump_controller as integration
from custom_components.fglair_heatpump_controller import (
    _LOGIN_BACKOFF_MAX,
    _LOGIN_BACKOFF_MIN,
    _LOGIN_REUSE,
    _LOGIN_STATE,
    _install_login_guard,
)
from custom_components.fglair_heatpump_controller.const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DOMAIN,
)


class _Clock:
    """Controllable replacement for time.monotonic()."""

    def __init__(self) -> None:
        """Start at an arbitrary point in time."""
        self.now = 1000.0

    def monotonic(self) -> float:
        """Return the current fake time."""
        return self.now


@pytest.fixture(autouse=True)
def clean_login_state() -> Iterator[None]:
    """Every test starts without remembered login state."""
    _LOGIN_STATE.clear()
    yield
    _LOGIN_STATE.clear()


@pytest.fixture
def clock() -> Iterator[_Clock]:
    """Replace the time module used by the login guard (not the global one)."""
    fake = _Clock()
    with patch.object(integration, "time", SimpleNamespace(monotonic=fake.monotonic)):
        yield fake


def _client(token: str | None = None) -> SimpleNamespace:
    """Fake library client whose login stores the token like the real one."""
    client = SimpleNamespace(_ACCESS_TOKEN_STR=token)

    async def login() -> str:
        client._ACCESS_TOKEN_STR = "fresh-token"
        return "fresh-token"

    client.login = AsyncMock(side_effect=login)
    client.async_authenticate = client.login
    return client


async def test_fresh_login_is_reused(clock: _Clock) -> None:
    """A login younger than the reuse time is shared instead of logging in again."""
    client = _client()
    _install_login_guard(client, "acc")

    assert await client.async_authenticate() == "fresh-token"
    clock.now += _LOGIN_REUSE - 1
    assert await client.async_authenticate() == "fresh-token"
    assert client.login.await_count == 1

    # older than the reuse time: real login again
    clock.now += 2
    assert await client.async_authenticate() == "fresh-token"
    assert client.login.await_count == 2


async def test_stored_token_of_new_client_is_not_trusted(clock: _Clock) -> None:
    """A token read from the token file is verified by a real login first."""
    client = _client(token="stored-token")
    _install_login_guard(client, "acc")
    assert await client.async_authenticate() == "fresh-token"
    assert client.login.await_count == 1


async def test_backoff_after_failed_login(
    clock: _Clock, caplog: pytest.LogCaptureFixture
) -> None:
    """After a failed login no login is attempted for a growing waiting time."""
    client = _client()
    client.login.side_effect = FGLairGeneralException
    _install_login_guard(client, "acc")

    with pytest.raises(FGLairGeneralException):
        await client.async_authenticate()
    assert _LOGIN_STATE["acc"]["backoff"] == _LOGIN_BACKOFF_MIN
    assert "next login attempt in 2 min" in caplog.text

    # within the waiting time: rejected without asking the cloud
    clock.now += _LOGIN_BACKOFF_MIN - 1
    with pytest.raises(FGLairGeneralException):
        await client.async_authenticate()
    assert client.login.await_count == 1

    # after the waiting time: next attempt, failing again -> doubled waiting time
    expected = _LOGIN_BACKOFF_MIN
    while expected < _LOGIN_BACKOFF_MAX:
        clock.now += expected + 1
        with pytest.raises(FGLairGeneralException):
            await client.async_authenticate()
        expected = min(_LOGIN_BACKOFF_MAX, expected * 2)
        assert _LOGIN_STATE["acc"]["backoff"] == expected

    # capped at the maximum
    clock.now += _LOGIN_BACKOFF_MAX + 1
    with pytest.raises(FGLairGeneralException):
        await client.async_authenticate()
    assert _LOGIN_STATE["acc"]["backoff"] == _LOGIN_BACKOFF_MAX


async def test_success_after_failure_resets_backoff(
    clock: _Clock, caplog: pytest.LogCaptureFixture
) -> None:
    """A successful login after failures ends the waiting time."""
    client = _client()
    original = client.login.side_effect
    client.login.side_effect = FGLairGeneralException
    _install_login_guard(client, "acc")
    with pytest.raises(FGLairGeneralException):
        await client.async_authenticate()

    client.login.side_effect = original
    clock.now += _LOGIN_BACKOFF_MIN + 1
    assert await client.async_authenticate() == "fresh-token"
    assert "FGLair login successful again" in caplog.text
    assert _LOGIN_STATE["acc"]["backoff"] == 0.0
    assert _LOGIN_STATE["acc"]["ok"] == clock.now


async def test_backoff_survives_a_new_client(clock: _Clock) -> None:
    """The waiting time is kept per account across reloads/retries."""
    first = _client()
    first.login.side_effect = FGLairGeneralException
    _install_login_guard(first, "acc")
    with pytest.raises(FGLairGeneralException):
        await first.async_authenticate()

    second = _client()
    _install_login_guard(second, "acc")
    with pytest.raises(FGLairGeneralException):
        await second.async_authenticate()
    second.login.assert_not_awaited()

    # other accounts are not affected
    other = _client()
    _install_login_guard(other, "other")
    assert await other.async_authenticate() == "fresh-token"


async def test_only_one_login_at_a_time(clock: _Clock) -> None:
    """Concurrent requests wait for the running login and share its token."""
    client = _client()
    release = asyncio.Event()
    calls: list[Any] = []

    async def slow_login() -> str:
        calls.append(None)
        await release.wait()
        client._ACCESS_TOKEN_STR = "fresh-token"
        return "fresh-token"

    client.login.side_effect = slow_login
    _install_login_guard(client, "acc")

    tasks = [asyncio.ensure_future(client.async_authenticate()) for _ in range(3)]
    await asyncio.sleep(0)
    assert len(calls) == 1
    release.set()
    assert await asyncio.gather(*tasks) == ["fresh-token"] * 3
    assert len(calls) == 1


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_setup_not_ready_without_device_list(hass: HomeAssistant) -> None:
    """Device list not available (cloud/login problem): setup is retried later."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="user@example.com",
        data={
            CONF_USERNAME: "user@example.com",
            CONF_PASSWORD: "secret",
            CONF_REGION: "eu",
            CONF_TOKENPATH: "token.txt",
            CONF_TEMPERATURE_OFFSET: 0.0,
        },
    )
    entry.add_to_hass(hass)
    client = MagicMock()
    client.async_authenticate = AsyncMock(return_value="token")
    client.async_get_devices_dsn = AsyncMock(side_effect=FGLairGeneralException)
    with patch(
        "custom_components.fglair_heatpump_controller.FGLairApiClient",
        return_value=client,
    ) as factory:
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_RETRY
    # one shared client, wrapped by the login guard
    factory.assert_called_once()
    assert "user@example.com" in _LOGIN_STATE
    assert entry.entry_id not in hass.data.get(DOMAIN, {})
