"""Connectivity of FGLair devices.

* ``Connectivity`` (name translated by Home Assistant): the device reported to the
  FGLair cloud recently - based on a fresh poll AND a recent report of the device. Off
  means: the unit itself is silent, although the cloud answers.
* ``Cloud connection``: Home Assistant could poll the device from the FGLair cloud
  recently. Off means: cloud or login problem - nothing can be said about the unit
  itself.

Both are re-evaluated every minute, so they also turn off when no new data arrives at
all.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import utcnow

from .const import DOMAIN, SIGNAL_PROPERTIES, STALE_AFTER
from .sensor import device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the connectivity sensors as soon as a device has been polled once."""
    created: set[str] = set()

    @callback
    def _new_device(dsn: str, device_name: str | None, *_: Any) -> None:
        if dsn in created:
            return
        created.add(dsn)
        async_add_entities(
            [
                _DeviceConnectivity(hass, dsn, device_name),
                _CloudConnection(hass, dsn, device_name),
            ]
        )

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_PROPERTIES, _new_device)
    )
    for dsn, (name, *_rest) in list(
        hass.data.get(DOMAIN, {}).get("properties", {}).items()
    ):
        _new_device(dsn, name)


class _Base(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = True  # re-evaluate every minute, also without new data
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, hass: HomeAssistant, dsn: str, device_name: str | None, key: str
    ) -> None:
        self._hass_ref = hass
        self._dsn = dsn
        self._attr_unique_id = f"{dsn}_{key}"
        self._attr_device_info = device_info(dsn, device_name)

    def _status(self) -> dict[str, Any]:
        return self._hass_ref.data.get(DOMAIN, {}).get("status", {}).get(self._dsn, {})


class _CloudConnection(_Base):
    _attr_translation_key = "cloud_connection"
    _attr_icon = "mdi:cloud-check-outline"

    def __init__(self, hass: HomeAssistant, dsn: str, device_name: str | None) -> None:
        super().__init__(hass, dsn, device_name, "cloud_connection")

    async def async_update(self) -> None:
        poll = self._status().get("last_poll")
        self._attr_is_on = poll is not None and utcnow() - poll <= STALE_AFTER


class _DeviceConnectivity(_Base):
    # no _attr_name: Home Assistant uses the translated name of the device class
    # (_attr_name = None means "entity is the device" and shows the device name)

    def __init__(self, hass: HomeAssistant, dsn: str, device_name: str | None) -> None:
        super().__init__(hass, dsn, device_name, "connectivity")

    async def async_update(self) -> None:
        status = self._status()
        poll, contact = status.get("last_poll"), status.get("last_contact")
        if poll is None or utcnow() - poll > STALE_AFTER:
            # without a fresh poll nothing is known about the unit
            self._attr_is_on = None
            return
        self._attr_is_on = contact is not None and poll - contact <= STALE_AFTER
