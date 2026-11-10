"""Diagnostic sensors for FGLair devices.

The FGLair cloud returns every property of a device together with the time the device
last reported it (``data_updated_at``). The climate entity only uses a few of them. This
platform exposes, per device:

* ``Last contact`` - newest ``data_updated_at`` of all properties, i.e. when the device
  last reported anything to the cloud. If it stops advancing, the device has lost its
  cloud connection even though the climate entity still shows the last known state.
* ``Last change`` - when a property value last changed between two polls.
* one diagnostic sensor per further property with a real value (not 65535). Only a few
  useful ones are enabled by default, the others are created disabled and can be enabled
  in the UI.

The data comes from the climate entity's regular poll (dispatcher signal), no extra API
calls.
"""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_PROPERTIES

_LOGGER: logging.Logger = logging.getLogger(__package__)

_MAX_STATE = 255

# Enabled by default; all other properties are created disabled.
ENABLED = {"error_code", "op_status", "wifi_led_enable"}

# Properties the climate entity already shows - no extra sensor for them.
HANDLED = {
    "operation_mode",
    "adjust_temperature",
    "display_temperature",
    "fan_speed",
    "af_vertical_swing",
    "af_vertical_direction",
    "af_horizontal_swing",
    "af_horizontal_direction",
    "economy_mode",
    "powerful_mode",
    "min_heat",
    "refresh",
    "get_prop",
    "get_prop2",
}

NAMES = {
    "error_code": "Error code",
    "op_status": "Operation status",
    "wifi_led_enable": "Wi-Fi LED",
    "model_name": "Model",
    "mcu_fw_version": "Controller firmware",
    "oem_host_version": "Wi-Fi module firmware",
    "device_name": "Device name",
    "device_capabilities": "Device capabilities",
    "af_vertical_num_dir": "Vertical airflow positions",
    "af_horizontal_num_dir": "Horizontal airflow positions",
    "outdoor_temperature": "Outdoor temperature raw",
    "outdoor_low_noise": "Outdoor low noise",
    "human_det": "Human detection",
    "coil_dry_mode": "Coil dry mode",
    "external_thermostat_off": "External thermostat off",
    "heat_sterilizatio": "Heat sterilization",
    "comm_version": "Communication version",
    "ac_info1": "AC info 1",
    "monitor1": "Monitor 1",
    "monitor2": "Monitor 2",
    "ota_status": "OTA status",
}


def is_placeholder(value: Any) -> bool:
    """65535 (or a list of 65535/empty) means: not supported by this model."""
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return int(value) == 65535
    parts = str(value).replace(":", ",").split(",")
    return all(p.strip() in ("", "65535") for p in parts)


# Properties with a translated name (translations/*.json, entity.sensor.<key>.name).
# The cloud property "outdoor_temperature" is the raw value -> key
# "outdoor_temperature_raw".
TRANSLATED = {
    "error_code",
    "op_status",
    "wifi_led_enable",
    "model_name",
    "mcu_fw_version",
    "oem_host_version",
    "device_name",
    "device_capabilities",
    "af_vertical_num_dir",
    "af_horizontal_num_dir",
    "outdoor_low_noise",
    "human_det",
    "coil_dry_mode",
    "external_thermostat_off",
    "heat_sterilizatio",
    "comm_version",
    "ac_info1",
    "monitor1",
    "monitor2",
    "ota_status",
}


def translation_key(prop: str) -> str | None:
    """Return the translation key of a property sensor, if it has one."""
    if prop == "outdoor_temperature":
        return "outdoor_temperature_raw"
    return prop if prop in TRANSLATED else None


def display_name(name: str) -> str:
    """English display name of a property."""
    return NAMES.get(name) or name.replace("_", " ").strip().capitalize()


def _parse_time(text: Any) -> datetime | None:
    if not text:
        return None
    return dt_util.parse_datetime(str(text))


def device_info(dsn: str, device_name: str | None) -> DeviceInfo:
    """Device shared by the climate entity and the diagnostic sensors."""
    return DeviceInfo(
        identifiers={(DOMAIN, dsn)},
        name=device_name or dsn,
        manufacturer="Fujitsu General",
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the diagnostic sensors; entities are created when properties arrive."""
    manager = _DiagnosticsManager(async_add_entities)
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_PROPERTIES, manager.async_update)
    )
    for dsn, (name, properties, extras) in list(
        hass.data.get(DOMAIN, {}).get("properties", {}).items()
    ):
        manager.async_update(dsn, name, properties, extras)


class _DiagnosticsManager:
    """Creates and updates the sensors of all devices."""

    def __init__(self, async_add_entities: AddEntitiesCallback) -> None:
        self._add = async_add_entities
        self._entities: dict[tuple[str, str], _BaseSensor] = {}
        self._previous: dict[str, dict[str, Any]] = {}

    @callback
    def async_update(
        self,
        dsn: str,
        device_name: str | None,
        properties: Any,
        extras: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(properties, list):
            return
        values: dict[str, Any] = {}
        updated_at: dict[str, datetime] = {}
        for item in properties:
            prop = item.get("property") if isinstance(item, dict) else None
            if not isinstance(prop, dict) or "name" not in prop:
                continue
            values[prop["name"]] = prop.get("value")
            if (t := _parse_time(prop.get("data_updated_at"))) is not None:
                updated_at[prop["name"]] = t

        new: list[_BaseSensor] = []

        def entity(key: str, factory) -> _BaseSensor:
            if (dsn, key) not in self._entities:
                self._entities[(dsn, key)] = factory()
                new.append(self._entities[(dsn, key)])
            return self._entities[(dsn, key)]

        contact = entity(
            "last_contact",
            lambda: _TimestampSensor(
                dsn, device_name, "last_contact", "Last contact", "last_contact"
            ),
        )
        change = entity(
            "last_change",
            lambda: _TimestampSensor(
                dsn, device_name, "last_change", "Last change", "last_change"
            ),
        )
        poll = entity(
            "last_poll",
            lambda: _TimestampSensor(
                dsn, device_name, "last_poll", "Last poll", "last_poll"
            ),
        )
        extras = extras or {}
        if updated_at:
            contact.set_value(max(updated_at.values()))
        if extras.get("last_poll") is not None:
            poll.set_value(extras["last_poll"])
        indoor = entity(
            "indoor_temperature",
            lambda: _TemperatureSensor(
                dsn,
                device_name,
                "indoor_temperature",
                "Indoor temperature",
                "indoor_temperature",
            ),
        )
        indoor.set_value(extras.get("indoor"))
        if (
            extras.get("outdoor") is not None
            or (dsn, "outdoor_temperature_c") in self._entities
        ):
            outdoor = entity(
                "outdoor_temperature_c",
                lambda: _TemperatureSensor(
                    dsn,
                    device_name,
                    "outdoor_temperature_c",
                    "Outdoor temperature",
                    "outdoor_temperature",
                ),
            )
            outdoor.set_value(extras.get("outdoor"))
        previous = self._previous.get(dsn)
        if previous is not None:
            changed = [n for n, v in values.items() if previous.get(n) != v]
            if changed:
                times = [updated_at[n] for n in changed if n in updated_at]
                change.set_value(max(times) if times else dt_util.utcnow())
        self._previous[dsn] = values

        for name, value in values.items():
            if name in HANDLED or is_placeholder(value):
                continue
            sensor = entity(name, lambda n=name: _PropertySensor(dsn, device_name, n))
            sensor.set_value(value)

        if new:
            self._add(new)
        for sensor in self._entities.values():
            # only entities that are active in HA (not disabled/removed)
            if sensor.dsn == dsn and sensor.active and sensor not in new:
                sensor.async_write_ha_state()


class _BaseSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        dsn: str,
        device_name: str | None,
        key: str,
        name: str,
        tkey: str | None = None,
    ) -> None:
        self.dsn = dsn
        self.active = False
        self._attr_unique_id = f"{dsn}_{key}"
        if tkey:
            # name from the translations (translations/*.json)
            self._attr_translation_key = tkey
        else:
            self._attr_name = name
        self._attr_device_info = device_info(dsn, device_name)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.active = True

    async def async_will_remove_from_hass(self) -> None:
        # e.g. disabled in the UI: do not write values afterwards
        self.active = False
        await super().async_will_remove_from_hass()

    def set_value(self, value: Any) -> None:
        raise NotImplementedError


class _TimestampSensor(_BaseSensor, RestoreSensor):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def set_value(self, value: datetime) -> None:
        self._attr_native_value = value

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self._attr_native_value is None and (
            last := await self.async_get_last_sensor_data()
        ):
            self._attr_native_value = (
                last.native_value
                if isinstance(last.native_value, datetime)
                else _parse_time(last.native_value)
            )


class _TemperatureSensor(_BaseSensor):
    """Indoor/outdoor temperature as a regular temperature sensor (not diagnostic)."""

    _attr_entity_category = None
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1

    def set_value(self, value: Any) -> None:
        self._attr_native_value = value if isinstance(value, (int, float)) else None


class _PropertySensor(_BaseSensor):
    def __init__(self, dsn: str, device_name: str | None, prop: str) -> None:
        super().__init__(
            dsn, device_name, prop, display_name(prop), translation_key(prop)
        )
        self._attr_entity_registry_enabled_default = prop in ENABLED
        if prop == "error_code":
            self._attr_icon = "mdi:alert-circle-outline"

    def set_value(self, value: Any) -> None:
        text = (
            value
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            else str(value)
        )
        if isinstance(text, str) and len(text) > _MAX_STATE:
            self._attr_extra_state_attributes = {"value": text}
            text = text[: _MAX_STATE - 1] + "…"
        self._attr_native_value = text
