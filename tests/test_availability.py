"""Availability of the climate entity: fresh poll and recent report of the unit."""

from datetime import timedelta
from typing import Any
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.fglair_heatpump_controller.climate import (
    FujitsuClimate,
    _newest_report,
    device_is_available,
)
from custom_components.fglair_heatpump_controller.const import (
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    STALE_AFTER,
)

SECOND = timedelta(seconds=1)


def _item(name: str, stamp: str | None) -> dict[str, Any]:
    """One entry of the FGLair property list."""
    prop: dict[str, Any] = {"name": name, "value": 1}
    if stamp is not None:
        prop["data_updated_at"] = stamp
    return {"property": prop}


def test_device_is_available() -> None:
    """Fresh poll and a report of the unit shortly before it."""
    now = dt_util.utcnow()
    # never polled / poll too old
    assert device_is_available(None, None) is False
    assert device_is_available(now - STALE_AFTER - SECOND, now) is False
    # fresh poll, no report time known
    assert device_is_available(now, None) is True
    # fresh poll, unit reported recently
    assert device_is_available(now, now - STALE_AFTER) is True
    # fresh poll, but the unit has been silent for too long
    assert device_is_available(now, now - STALE_AFTER - SECOND) is False


def test_newest_report() -> None:
    """Newest data_updated_at of all properties, invalid entries are skipped."""
    assert _newest_report(None) is None
    assert _newest_report({"property": {}}) is None
    assert _newest_report([]) is None
    properties = [
        "garbage",
        {"no_property": 1},
        {"property": "garbage"},
        _item("no_stamp", None),
        _item("empty_stamp", ""),
        _item("bad_stamp", "not a date"),
        _item("a", "2026-11-09T10:00:00Z"),
        _item("b", "2026-11-09T10:05:00Z"),
        _item("c", "2026-11-09T09:00:00Z"),
    ]
    newest = _newest_report(properties)
    assert newest == dt_util.parse_datetime("2026-11-09T10:05:00Z")


def _available(entity: FujitsuClimate) -> bool:
    """Read the availability anew (the state changes between the reads)."""
    return entity.available


def test_climate_available(hass: HomeAssistant) -> None:
    """The climate entity follows device_is_available."""
    entity = FujitsuClimate(
        fglair_api_client=MagicMock(),
        dsn="dsn1",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=hass,
        coordinator=MagicMock(),
    )
    # not polled yet
    assert _available(entity) is False

    now = dt_util.utcnow()
    entity._last_poll = now
    entity._last_contact = now - timedelta(minutes=1)
    assert _available(entity) is True

    # the unit stopped reporting to the cloud although the cloud answers
    entity._last_contact = now - STALE_AFTER - SECOND
    assert _available(entity) is False

    # no successful poll for too long (cloud or login problem)
    entity._last_contact = None
    entity._last_poll = now - STALE_AFTER - SECOND
    assert _available(entity) is False
