"""Upstream energy meter per device (optional, set in the integration options).

The air conditioners do not measure their own consumption. If a meter in front of a
device is configured (energy counter in kWh/Wh, or a power sensor in W), this module

* splits the measured energy by operating mode into six counters (heating, cooling,
  drying, fan, standby, total), see sensor.py, and
* provides the measured power, from which the climate entity derives its real
  hvac_action (compressor running or idle, and in auto mode heating or cooling).

The operating mode comes from the climate entity of the same device. FGLair reports mode
changes with a delay of about 45 s; energy around a mode change may therefore be
assigned to the previous mode for that short time.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import logging
from typing import Any

from homeassistant.components.climate.const import HVACMode
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import (
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

_LOGGER: logging.Logger = logging.getLogger(__package__)

BUCKETS = ("heat", "cool", "dry", "fan", "standby")

# Plausibility: a single step of an energy counter above this is treated as a counter
# exchange/glitch and ignored (kWh)
MAX_STEP_KWH = 5.0
# Power sensors: longest time a power value is assumed to stay constant (s)
MAX_POWER_GAP = 3600


def _number(state: State | None) -> float | None:
    if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN, ""):
        return None
    try:
        return float(state.state)
    except ValueError:
        return None


def _kind(state: State | None) -> str | None:
    """'energy' or 'power' from device class / unit of a state."""
    if state is None:
        return None
    attrs = state.attributes
    unit = str(attrs.get("unit_of_measurement") or "")
    dclass = attrs.get("device_class")
    if dclass == "energy" or unit in ("kWh", "Wh", "MWh"):
        return "energy"
    if dclass == "power" or unit in ("W", "kW"):
        return "power"
    return None


def _unit(state: State | None) -> str:
    """Return the unit of measurement of a state ("" if unknown)."""
    if state is None:
        return ""
    return str(state.attributes.get("unit_of_measurement") or "")


def _to_kwh(value: float, unit: str) -> float:
    return value / 1000 if unit == "Wh" else value * 1000 if unit == "MWh" else value


def _to_w(value: float, unit: str) -> float:
    return value * 1000 if unit == "kW" else value


def find_power_sibling(hass: HomeAssistant, entity_id: str) -> str | None:
    """Power sensor on the same device as an energy counter (e.g. the smart plug)."""
    reg = er.async_get(hass)
    entry = reg.async_get(entity_id)
    if entry is None or entry.device_id is None:
        return None
    for other in er.async_entries_for_device(reg, entry.device_id):
        if (
            other.domain != "sensor"
            or other.entity_id == entity_id
            or other.disabled_by
        ):
            continue
        if (other.device_class or other.original_device_class) == "power" or _kind(
            hass.states.get(other.entity_id)
        ) == "power":
            return other.entity_id
    return None


class UpstreamMeter:
    """Follows the configured meter of one device."""

    def __init__(
        self, hass: HomeAssistant, dsn: str, entity_id: str, threshold: float
    ) -> None:
        """Initialize the meter of one device."""
        self.hass = hass
        self.dsn = dsn
        self.source = entity_id
        self.threshold = threshold
        self.energy_id: str | None = None
        self.power_id: str | None = None
        self.power: float | None = None
        self._last_energy: float | None = None  # kWh
        self._last_power_time: datetime | None = None
        # set by the climate entity: () -> (hvac_mode, target, current)
        self.mode_provider: (
            Callable[[], tuple[Any, float | None, float | None]] | None
        ) = None
        # energy sensors (sensor.py) register here: (bucket, kwh) -> None
        self._energy_listeners: list[Callable[[str, float], None]] = []
        self._power_listeners: list[Callable[[], None]] = []
        self._unsub: Callable[[], None] | None = None
        self._auto_direction = "heat"

    # ------------------------------------------------------------------ setup
    @callback
    def async_start(self) -> None:
        """Find the energy/power entities and start following them."""
        kind = _kind(self.hass.states.get(self.source))
        if kind == "power":
            self.power_id = self.source
        else:
            # Energy counter (or not yet known - then treated as energy counter)
            self.energy_id = self.source
            self.power_id = find_power_sibling(self.hass, self.source)
        ids = [e for e in (self.energy_id, self.power_id) if e]
        _LOGGER.debug(
            "Meter %s: energy %s, power %s", self.dsn, self.energy_id, self.power_id
        )
        self._unsub = async_track_state_change_event(
            self.hass, ids, self._async_changed
        )
        if self.power_id:
            st = self.hass.states.get(self.power_id)
            if (v := _number(st)) is not None:
                self.power = _to_w(v, _unit(st))
                self._last_power_time = dt_util.utcnow()

    @callback
    def async_stop(self) -> None:
        """Stop following the meter."""
        if self._unsub:
            self._unsub()
            self._unsub = None

    def add_energy_listener(
        self, func: Callable[[str, float], None]
    ) -> Callable[[], None]:
        """Call func(bucket, kwh) for every energy step; returns the remove function."""
        self._energy_listeners.append(func)
        return lambda: self._energy_listeners.remove(func)

    def add_power_listener(self, func: Callable[[], None]) -> Callable[[], None]:
        """Call func() for every new power value; returns the remove function."""
        self._power_listeners.append(func)
        return lambda: self._power_listeners.remove(func)

    def restore_last_energy(self, value: float | None) -> None:
        """Set the starting point of the counting.

        value = counter reading stored before a restart (with the total sensor): the
        energy used while Home Assistant was down is then counted with the next reading.
        Without a stored reading the current reading is the starting point.
        """
        if self._last_energy is not None or self.energy_id is None:
            return
        if value is None:
            st = self.hass.states.get(self.energy_id)
            if (v := _number(st)) is not None:
                value = _to_kwh(v, _unit(st))
        self._last_energy = value

    @property
    def last_energy(self) -> float | None:
        """Last counter reading in kWh."""
        return self._last_energy

    # ------------------------------------------------------------------ mode
    def running(self) -> bool | None:
        """Compressor running according to the measured power (None = unknown)."""
        if self.power is None:
            return None
        return self.power >= self.threshold

    def bucket(self) -> str:
        """Counter the energy of right now belongs to."""
        if self.mode_provider is None:
            return "standby"
        mode, target, current = self.mode_provider()
        if mode in (None, HVACMode.OFF):
            return "standby"
        if mode == HVACMode.HEAT:
            return "heat"
        if mode == HVACMode.COOL:
            return "cool"
        if mode == HVACMode.DRY:
            return "dry"
        if mode == HVACMode.FAN_ONLY:
            return "fan"
        # auto (heat_cool): direction from target vs. room temperature; keep the last
        # one inside a small band so a reading of exactly the target does not flip it
        if target is not None and current is not None:
            if current < target - 0.25:
                self._auto_direction = "heat"
            elif current > target + 0.25:
                self._auto_direction = "cool"
        return self._auto_direction

    # ------------------------------------------------------------------ events
    @callback
    def _async_changed(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        eid = event.data["entity_id"]
        if eid == self.power_id:
            self._power_changed(new, old)
        if eid == self.energy_id:
            self._energy_changed(new)

    def _power_changed(self, new: State | None, old: State | None) -> None:
        now = dt_util.utcnow()
        unit = _unit(new or old)
        value = _number(new)
        if (
            self.energy_id is None
            and self.power is not None
            and self._last_power_time is not None
        ):
            # No energy counter: integrate the previous power value over the elapsed
            # time
            dt = min((now - self._last_power_time).total_seconds(), MAX_POWER_GAP)
            if dt > 0:
                self._add(self.power * dt / 3_600_000)
        self.power = _to_w(value, unit) if value is not None else None
        self._last_power_time = now
        for func in list(self._power_listeners):
            func()

    def _energy_changed(self, new: State | None) -> None:
        value = _number(new)
        if value is None:
            return  # keep the last reading; the next valid one continues from there
        kwh = _to_kwh(value, _unit(new))
        last, self._last_energy = self._last_energy, kwh
        if last is None:
            return
        delta = kwh - last
        if delta < 0:
            # counter reset (e.g. plug replaced/reset): the new reading is the energy
            # since then
            delta = kwh
        if delta > MAX_STEP_KWH:
            _LOGGER.warning(
                "Meter %s: implausible step of %.3f kWh on %s ignored",
                self.dsn,
                delta,
                self.energy_id,
            )
            return
        if delta > 0:
            self._add(delta)

    def _add(self, kwh: float) -> None:
        bucket = self.bucket()
        for func in list(self._energy_listeners):
            func(bucket, kwh)
