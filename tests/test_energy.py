"""Upstream meter: energy per operating mode and hvac_action from the measured power."""

from collections.abc import Iterable, Iterator
from functools import partial
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.climate.const import HVACAction, HVACMode
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity import Entity
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_restore_cache_with_extra_data,
)

from custom_components.fglair_heatpump_controller import climate
from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from custom_components.fglair_heatpump_controller.const import (
    CONF_ACTION_THRESHOLD,
    CONF_METERS,
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
)
from custom_components.fglair_heatpump_controller.energy import (
    UpstreamMeter,
    _kind,
    _number,
    _unit,
    find_power_sibling,
)
from custom_components.fglair_heatpump_controller.sensor import (
    _EnergyManager,
    _EnergySensor,
)

E = "sensor.plug_energy"
P = "sensor.plug_power"


def _action(entity: FujitsuClimate) -> HVACAction | None:
    """Read hvac_action anew (it changes with the measured power)."""
    return entity.hvac_action


def _last_energy(meter: UpstreamMeter) -> float | None:
    """Read the starting point anew (it changes with new readings)."""
    return meter.last_energy


def _get(hass: HomeAssistant, entity_id: str | None) -> State:
    """State of an entity that has to exist."""
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None, entity_id
    return state


def _uid(entity: Entity) -> str:
    """Return the unique id of an entity that has one."""
    assert entity.unique_id is not None
    return entity.unique_id


def _plug(hass: HomeAssistant) -> None:
    """Smart plug with energy counter and power sensor on one device."""
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    dev = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={("test", "plug")}
    )
    reg = er.async_get(hass)
    reg.async_get_or_create(
        "sensor",
        "test",
        "e",
        device_id=dev.id,
        suggested_object_id="plug_energy",
        original_device_class="energy",
    )
    reg.async_get_or_create(
        "sensor",
        "test",
        "p",
        device_id=dev.id,
        suggested_object_id="plug_power",
        original_device_class="power",
    )
    hass.states.async_set(
        E, "100.0", {"unit_of_measurement": "kWh", "device_class": "energy"}
    )
    hass.states.async_set(P, "5", {"unit_of_measurement": "W", "device_class": "power"})


async def test_energy_split_by_mode(hass: HomeAssistant) -> None:
    """Energy steps are assigned to the counter of the current operating mode."""
    _plug(hass)
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    mode: dict[str, Any] = {"m": HVACMode.HEAT, "t": 22.0, "c": 19.0}
    meter.mode_provider = lambda: (mode["m"], mode["t"], mode["c"])
    meter.async_start()
    assert meter.energy_id == E and meter.power_id == P
    meter.restore_last_energy(None)  # starting point = current reading
    got: list[tuple[str, float]] = []
    meter.add_energy_listener(lambda b, k: got.append((b, round(k, 4))))

    hass.states.async_set(E, "100.5", {"unit_of_measurement": "kWh"})
    mode["m"] = HVACMode.COOL
    hass.states.async_set(E, "100.75", {"unit_of_measurement": "kWh"})
    mode["m"] = HVACMode.OFF
    hass.states.async_set(E, "100.76", {"unit_of_measurement": "kWh"})
    hass.states.async_set(E, "unavailable", {})
    mode["m"] = HVACMode.FAN_ONLY
    hass.states.async_set(
        E, "100.86", {"unit_of_measurement": "kWh"}
    )  # continues after the gap
    mode["m"] = HVACMode.DRY
    hass.states.async_set(E, "0.2", {"unit_of_measurement": "kWh"})  # counter reset
    hass.states.async_set(E, "50", {"unit_of_measurement": "kWh"})  # implausible step
    # auto: room colder than target -> heat, warmer -> cool
    mode["m"] = HVACMode.AUTO
    hass.states.async_set(E, "50.1", {"unit_of_measurement": "kWh"})
    mode["c"] = 24.0
    hass.states.async_set(E, "50.3", {"unit_of_measurement": "kWh"})
    await hass.async_block_till_done()
    assert got == [
        ("heat", 0.5),
        ("cool", 0.25),
        ("standby", 0.01),
        ("fan", 0.1),
        ("dry", 0.2),
        ("heat", 0.1),
        ("cool", 0.2),
    ]
    meter.async_stop()


async def test_restore_counts_downtime(hass: HomeAssistant) -> None:
    """Energy used while Home Assistant was down is counted with the next reading."""
    _plug(hass)
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    meter.mode_provider = lambda: (HVACMode.HEAT, 22.0, 20.0)
    meter.async_start()
    meter.restore_last_energy(99.0)  # reading stored before the restart
    got: list[tuple[str, float]] = []
    meter.add_energy_listener(lambda b, k: got.append((b, round(k, 4))))
    hass.states.async_set(E, "100.2", {"unit_of_measurement": "kWh"})
    await hass.async_block_till_done()
    assert got == [("heat", 1.2)]


async def test_power_only_integrates(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Without an energy counter the power is integrated over time."""
    hass.states.async_set(
        P, "1000", {"unit_of_measurement": "W", "device_class": "power"}
    )
    meter = UpstreamMeter(hass, "dsn1", P, 150)
    meter.mode_provider = lambda: (HVACMode.HEAT, 22.0, 20.0)
    meter.async_start()
    assert meter.energy_id is None and meter.power_id == P and meter.running() is True
    got: list[tuple[str, float]] = []
    meter.add_energy_listener(lambda b, k: got.append((b, round(k, 4))))
    freezer.tick(1800)
    hass.states.async_set(P, "10", {"unit_of_measurement": "W"})
    await hass.async_block_till_done()
    assert got == [("heat", 0.5)]
    assert meter.running() is False


def _climate(
    hass: HomeAssistant, mode_value: int, desc: str, op: str = "Normal"
) -> FujitsuClimate:
    """Climate entity with a mocked operating mode and operation status."""
    c = FujitsuClimate(
        fglair_api_client=MagicMock(),
        dsn="dsn1",
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=hass,
        coordinator=MagicMock(),
    )
    c._fujitsu_device.get_operation_mode = MagicMock(return_value={"value": mode_value})
    c._fujitsu_device.get_operation_mode_desc = MagicMock(return_value=desc)
    c._fujitsu_device.get_op_status_desc = MagicMock(return_value=op)
    return c


async def test_hvac_action_from_power(hass: HomeAssistant) -> None:
    """hvac_action follows the measured power of the upstream meter."""
    _plug(hass)
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    meter.async_start()
    hass.data.setdefault(DOMAIN, {})["meters"] = {"dsn1": meter}
    heat = _climate(hass, 1, "heat")
    meter.mode_provider = lambda: (heat.hvac_mode, 22.0, 20.0)
    assert heat.hvac_mode == HVACMode.HEAT
    meter.power = 5
    assert _action(heat) == HVACAction.IDLE
    meter.power = 900
    assert _action(heat) == HVACAction.HEATING
    assert _climate(hass, 1, "heat", op="Defrost").hvac_action == HVACAction.PREHEATING
    cool = _climate(hass, 1, "cool")
    assert cool.hvac_action == HVACAction.COOLING
    fan = _climate(hass, 1, "fan_only")
    meter.power = 70
    assert fan.hvac_action == HVACAction.FAN
    auto = _climate(hass, 1, "auto")
    meter.mode_provider = lambda: (HVACMode.AUTO, 22.0, 25.0)
    meter.power = 400
    assert _action(auto) == HVACAction.COOLING
    meter.mode_provider = lambda: (HVACMode.AUTO, 22.0, 19.0)
    assert _action(auto) == HVACAction.HEATING
    # without meter: as before (mode only)
    hass.data[DOMAIN]["meters"] = {}
    meter.power = 5
    assert _action(heat) == HVACAction.HEATING


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_options_flow(hass: HomeAssistant) -> None:
    """One meter field per device plus the power threshold."""
    _plug(hass)
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={CONF_METERS: {"dsn2": P}})
    entry.add_to_hass(hass)
    coord = MagicMock()
    coord.devices = ["dsn1", "dsn2"]
    hass.data[DOMAIN] = {
        entry.entry_id: coord,
        "properties": {
            "dsn1": ("Schlafzimmer", [], {}),
            "dsn2": ("Wohnzimmer", [], {}),
        },
    }
    r = await hass.config_entries.options.async_init(entry.entry_id)
    assert r["type"] == "form"
    schema = r["data_schema"]
    assert schema is not None
    keys = [str(k) for k in schema.schema]
    assert keys == ["Schlafzimmer", "Wohnzimmer", CONF_ACTION_THRESHOLD]
    r = await hass.config_entries.options.async_configure(
        r["flow_id"], {"Schlafzimmer": E, CONF_ACTION_THRESHOLD: 200}
    )
    assert r["type"] == "create_entry"
    assert entry.options[CONF_METERS] == {"dsn1": E}
    assert entry.options[CONF_ACTION_THRESHOLD] == 200


async def test_energy_sensors(hass: HomeAssistant) -> None:
    """Six energy counters per device with a meter, created once."""
    _plug(hass)
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    meter.mode_provider = lambda: (HVACMode.COOL, 22.0, 25.0)
    meter.async_start()
    hass.data.setdefault(DOMAIN, {})["meters"] = {"dsn1": meter}
    added: list[_EnergySensor] = []

    def add_entities(
        new_entities: Iterable[Entity], update_before_add: bool = False
    ) -> None:
        for entity in new_entities:
            assert isinstance(entity, _EnergySensor)
            added.append(entity)

    mgr = _EnergyManager(hass, add_entities)
    mgr.async_update("dsn1", "Schlafzimmer", [], {})
    mgr.async_update("dsn1", "Schlafzimmer", [], {})  # only once
    mgr.async_update("dsn9", "ohne Zaehler", [], {})
    assert sorted(_uid(e) for e in added) == sorted(
        f"dsn1_energy_{b}" for b in ("heat", "cool", "dry", "fan", "standby", "total")
    )
    for e in added:
        meter.add_energy_listener(e._async_add)
    meter.restore_last_energy(None)
    hass.states.async_set(E, "100.4", {"unit_of_measurement": "kWh"})
    await hass.async_block_till_done()
    werte = {_uid(e).split("_energy_")[1]: e.native_value for e in added}
    assert werte == {
        "heat": 0.0,
        "cool": 0.4,
        "dry": 0.0,
        "fan": 0.0,
        "standby": 0.0,
        "total": 0.4,
    }
    total = next(e for e in added if _uid(e).endswith("total"))
    total._update_attrs()
    attributes = total.extra_state_attributes
    assert attributes is not None
    assert attributes["source_reading"] == 100.4


def test_helpers() -> None:
    """Numbers and kind (energy/power) of a meter state."""
    assert _number(None) is None
    assert _number(State(E, "unknown")) is None
    assert _number(State(E, "abc")) is None
    assert _number(State(E, "1.5")) == 1.5
    assert _kind(None) is None
    assert _kind(State(E, "1", {"unit_of_measurement": "Wh"})) == "energy"
    assert _kind(State(P, "1", {"unit_of_measurement": "kW"})) == "power"
    assert _kind(State(P, "1", {"unit_of_measurement": "%"})) is None
    assert _unit(None) == ""
    assert _unit(State(P, "1")) == ""
    assert _unit(State(P, "1", {"unit_of_measurement": "kW"})) == "kW"


async def test_find_power_sibling(hass: HomeAssistant) -> None:
    """Power sensor on the device of the energy counter, if there is one."""
    _plug(hass)
    assert find_power_sibling(hass, E) == P
    # not in the entity registry
    assert find_power_sibling(hass, "sensor.unknown") is None
    # registered without a device
    reg = er.async_get(hass)
    lonely = reg.async_get_or_create(
        "sensor", "test", "lonely", suggested_object_id="lonely"
    )
    assert find_power_sibling(hass, lonely.entity_id) is None
    # device without a power sensor (other sensors are skipped)
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    dev = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={("test", "counter")}
    )
    counter = reg.async_get_or_create(
        "sensor", "test", "c", device_id=dev.id, suggested_object_id="counter"
    )
    reg.async_get_or_create(
        "sensor", "test", "v", device_id=dev.id, suggested_object_id="voltage"
    )
    reg.async_get_or_create(
        "switch", "test", "s", device_id=dev.id, suggested_object_id="relay"
    )
    reg.async_get_or_create(
        "sensor",
        "test",
        "off",
        device_id=dev.id,
        suggested_object_id="disabled_power",
        original_device_class="power",
        disabled_by=er.RegistryEntryDisabler.USER,
    )
    assert find_power_sibling(hass, counter.entity_id) is None
    # power detected from the state (unit) instead of the registry
    reg.async_get_or_create(
        "sensor", "test", "w", device_id=dev.id, suggested_object_id="watts"
    )
    hass.states.async_set("sensor.watts", "3", {"unit_of_measurement": "W"})
    assert find_power_sibling(hass, counter.entity_id) == "sensor.watts"


async def test_meter_defaults(hass: HomeAssistant) -> None:
    """Unknown power and mode; starting point taken from the first reading."""
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    assert meter.running() is None
    assert meter.bucket() == "standby"
    meter.mode_provider = lambda: (None, None, None)
    assert meter.bucket() == "standby"
    # auto without temperatures: last direction (heat at the start)
    meter.mode_provider = lambda: (HVACMode.AUTO, None, None)
    assert meter.bucket() == "heat"

    # meter entity unknown yet: treated as energy counter
    meter.async_start()
    assert meter.energy_id == E and meter.power_id is None
    got: list[tuple[str, float]] = []
    meter.add_energy_listener(lambda b, k: got.append((b, round(k, 4))))
    # first reading without a restored one: only the starting point
    hass.states.async_set(E, "10", {"unit_of_measurement": "Wh"})
    hass.states.async_set(E, "1010", {"unit_of_measurement": "Wh"})
    await hass.async_block_till_done()
    assert meter.last_energy == 1.01
    assert got == [("heat", 1.0)]
    # an already known starting point is not replaced
    meter.restore_last_energy(5.0)
    assert meter.last_energy == 1.01
    meter.async_stop()
    meter.async_stop()  # twice is harmless

    # power meter: no energy starting point at all
    power = UpstreamMeter(hass, "dsn2", P, 150)
    hass.states.async_set(P, "2", {"unit_of_measurement": "kW"})
    power.async_start()
    assert power.power == 2000
    power.restore_last_energy(None)
    assert power.last_energy is None
    power.async_stop()


async def test_restore_without_reading(hass: HomeAssistant) -> None:
    """Without a stored and a current reading the counting starts later."""
    hass.states.async_set(E, "unavailable", {"device_class": "energy"})
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    meter.async_start()
    meter.restore_last_energy(None)
    assert _last_energy(meter) is None
    hass.states.async_set(E, "2", {"unit_of_measurement": "MWh"})
    await hass.async_block_till_done()
    assert _last_energy(meter) == 2000
    meter.async_stop()


async def test_power_listeners(hass: HomeAssistant) -> None:
    """Power listeners are called for every new power value, also when removed."""
    _plug(hass)
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    meter.async_start()
    calls: list[float | None] = []
    remove = meter.add_power_listener(lambda: calls.append(meter.power))
    hass.states.async_set(P, "900", {"unit_of_measurement": "W"})
    await hass.async_block_till_done()
    hass.states.async_remove(P)
    await hass.async_block_till_done()
    assert calls == [900.0, None]
    remove()
    hass.states.async_set(P, "1", {"unit_of_measurement": "W"})
    await hass.async_block_till_done()
    assert calls == [900.0, None]
    meter.async_stop()


async def test_hvac_action_drying(hass: HomeAssistant) -> None:
    """Dry mode with the compressor running."""
    _plug(hass)
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    meter.async_start()
    hass.data.setdefault(DOMAIN, {})["meters"] = {"dsn1": meter}
    dry = _climate(hass, 1, "dry")
    meter.power = 400
    assert _action(dry) == HVACAction.DRYING
    meter.power = 5
    assert _action(dry) == HVACAction.IDLE


def test_energy_sensor_ignores_property_poll(hass: HomeAssistant) -> None:
    """Energy sensors are only fed by the meter."""
    meter = UpstreamMeter(hass, "dsn1", E, 150)
    sensor = _EnergySensor("dsn1", None, meter, "heat")
    sensor.set_value(42)
    assert sensor.native_value == 0.0
    # other buckets do not count
    sensor._async_add("cool", 1.0)
    assert sensor.native_value == 0.0
    sensor._async_add("heat", 1.0)
    assert sensor.native_value == 1.0


# ---------------------------------------------------------------- end to end

DSN = "AC000W000000001"


def _properties() -> list[dict[str, Any]]:
    """Property list of a device in heating mode."""
    stamp = dt_util.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    props: dict[str, Any] = {
        "device_name": "AC",
        "operation_mode": 6,  # heat
        "adjust_temperature": 220,
        "display_temperature": 7000,
        "fan_speed": 0,
        "economy_mode": 0,
        "powerful_mode": 0,
        "min_heat": 0,
        "outdoor_low_noise": 0,
        "af_vertical_swing": 0,
        "af_vertical_direction": 1,
        "af_vertical_num_dir": 4,
        "af_horizontal_swing": 0,
        "af_horizontal_direction": 1,
        "af_horizontal_num_dir": 4,
        "refresh": 0,
    }
    return [
        {"property": {"name": n, "value": v, "key": i, "data_updated_at": stamp}}
        for i, (n, v) in enumerate(props.items())
    ]


@pytest.fixture
def mock_client() -> Iterator[MagicMock]:
    """Fake FGLair API client with one device."""
    client = MagicMock()
    client.async_authenticate = AsyncMock(return_value="token")
    client.async_get_devices_dsn = AsyncMock(return_value=[DSN])
    client.async_get_device_properties = AsyncMock(side_effect=lambda _: _properties())
    client.async_get_device_property = AsyncMock(return_value=[])
    client.async_set_device_property = AsyncMock(return_value=None)
    with (
        patch(
            "custom_components.fglair_heatpump_controller.FGLairApiClient",
            return_value=client,
        ),
        patch.object(
            climate,
            "_async_retry_api_call",
            partial(climate._async_retry_api_call, delay=0),
        ),
    ):
        yield client


def _energy_id(hass: HomeAssistant, bucket: str, entry: MockConfigEntry) -> str:
    """Register an energy sensor in advance (fixed entity id for restoring)."""
    return (
        er.async_get(hass)
        .async_get_or_create(
            "sensor",
            DOMAIN,
            f"{DSN}_energy_{bucket}",
            suggested_object_id=f"ac_energy_{bucket}",
            config_entry=entry,
        )
        .entity_id
    )


@pytest.mark.usefixtures("enable_custom_integrations", "mock_client")
async def test_meter_end_to_end(hass: HomeAssistant) -> None:
    """Options -> meter -> energy sensors (restored) and hvac_action; reload."""
    _plug(hass)
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
        # a meter of a device that is not in the account is ignored
        options={CONF_METERS: {DSN: E, "gone": P}, CONF_ACTION_THRESHOLD: 150},
    )
    entry.add_to_hass(hass)
    heat, cool, dry, total = (
        _energy_id(hass, b, entry) for b in ("heat", "cool", "dry", "total")
    )
    unit = {"native_unit_of_measurement": "kWh"}
    mock_restore_cache_with_extra_data(
        hass,
        [
            (State(heat, "1.5"), {"native_value": 1.5, **unit}),
            (State(cool, "abc"), {"native_value": "abc", **unit}),
            (State(dry, "0"), {"native_value": [1], **unit}),
            (
                State(total, "3.0", {"source_reading": 99.0}),
                {"native_value": 3.0, **unit},
            ),
        ],
    )

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    meters = hass.data[DOMAIN]["meters"]
    assert list(meters) == [DSN]
    meter = meters[DSN]
    assert meter.energy_id == E and meter.power_id == P
    # restored values; the stored counter reading is the starting point
    assert float(_get(hass, heat).state) == 1.5
    assert float(_get(hass, cool).state) == 0.0
    assert float(_get(hass, dry).state) == 0.0
    assert float(_get(hass, total).state) == 3.0
    assert meter.last_energy == 99.0
    assert _get(hass, total).attributes["source"] == E

    # energy since the stored reading counts as heating (mode from the climate entity)
    hass.states.async_set(E, "100.5", {"unit_of_measurement": "kWh"})
    await hass.async_block_till_done()
    assert float(_get(hass, heat).state) == 3.0
    assert float(_get(hass, total).state) == 4.5
    assert _get(hass, total).attributes["source_reading"] == 100.5

    # every new power value updates hvac_action of the climate entity
    climate_id = er.async_get(hass).async_get_entity_id(
        "climate", DOMAIN, f"{DSN}_climate"
    )
    hass.states.async_set(P, "900", {"unit_of_measurement": "W"})
    await hass.async_block_till_done()
    assert _get(hass, climate_id).attributes["hvac_action"] == "heating"
    hass.states.async_set(P, "5", {"unit_of_measurement": "W"})
    await hass.async_block_till_done()
    assert _get(hass, climate_id).attributes["hvac_action"] == "idle"

    # options changed: the integration is reloaded without the meter
    hass.config_entries.async_update_entry(entry, options={CONF_METERS: {}})
    await hass.async_block_till_done()
    assert hass.data[DOMAIN]["meters"] == {}
    assert meter._unsub is None
    assert entry.state is ConfigEntryState.LOADED
    # hvac_action no longer derived from the (low) measured power
    assert _get(hass, climate_id).attributes.get("hvac_action") != "idle"
