"""Diagnostic, temperature and connectivity sensors of the FGLair devices."""

from collections.abc import Iterable, Iterator
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import partial
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from freezegun.api import FrozenDateTimeFactory
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_REGION,
    CONF_USERNAME,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.fglair_heatpump_controller import climate
from custom_components.fglair_heatpump_controller.binary_sensor import (
    _CloudConnection,
    _DeviceConnectivity,
)
from custom_components.fglair_heatpump_controller.climate import (
    FujitsuClimate,
    _outdoor_degree,
)
from custom_components.fglair_heatpump_controller.const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    SIGNAL_PROPERTIES,
    STALE_AFTER,
)
from custom_components.fglair_heatpump_controller.sensor import (
    _MAX_STATE,
    _BaseSensor,
    _DiagnosticsManager,
    _PropertySensor,
    _TemperatureSensor,
    device_info,
    display_name,
    is_placeholder,
    translation_key,
)

DSN = "AC000W000000001"
LONG = "x" * 300


def _stamp(when: datetime) -> str:
    """FGLair time format."""
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def _properties(stamp: str, **changes: Any) -> list[dict[str, Any]]:
    """FGLair property list as returned by the cloud (names read by SplitAC)."""
    props: dict[str, Any] = {
        "device_name": "Living Room",
        "operation_mode": 0,
        "adjust_temperature": 220,
        "display_temperature": 6200,
        "outdoor_temperature": 6550,
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
        "error_code": 0,
        "op_status": 0,
        "model_name": LONG,
        "monitor1": 65535,
        "refresh": 0,
    }
    props.update(changes)
    return [
        {
            "property": {
                "name": name,
                "value": value,
                "key": index,
                "data_updated_at": stamp,
            }
        }
        for index, (name, value) in enumerate(props.items())
    ]


@pytest.fixture
def payload() -> dict[str, list[dict[str, Any]]]:
    """Return the current property list per device (changed by the tests)."""
    return {DSN: _properties(_stamp(dt_util.utcnow()))}


@pytest.fixture
def mock_client(payload: dict[str, list[dict[str, Any]]]) -> Iterator[MagicMock]:
    """Fake FGLair API client used by the whole integration."""
    client = MagicMock()
    client.async_authenticate = AsyncMock(return_value="token")
    client.async_get_devices_dsn = AsyncMock(side_effect=lambda: list(payload))
    client.async_get_device_properties = AsyncMock(side_effect=lambda d: payload[d])
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


@pytest.fixture
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Config entry of one FGLair account."""
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
    return entry


def _eid(hass: HomeAssistant, platform: str, key: str) -> str:
    """Entity id of an entity of the device by its unique id suffix."""
    entity_id = er.async_get(hass).async_get_entity_id(platform, DOMAIN, f"{DSN}_{key}")
    assert entity_id is not None, key
    return entity_id


def _state(hass: HomeAssistant, platform: str, key: str) -> str | None:
    """State of an entity of the device (None if it has no state)."""
    state = hass.states.get(_eid(hass, platform, key))
    return state.state if state else None


def _float_state(hass: HomeAssistant, platform: str, key: str) -> float:
    """Numeric state of an entity of the device."""
    state = _state(hass, platform, key)
    assert state is not None, key
    return float(state)


def _entry(reg: er.EntityRegistry, entity_id: str) -> er.RegistryEntry:
    """Registry entry of an entity that has to exist."""
    entry = reg.async_get(entity_id)
    assert entry is not None, entity_id
    return entry


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_sensors_end_to_end(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
    payload: dict[str, list[dict[str, Any]]],
) -> None:
    """Climate poll -> dispatcher -> sensors and connectivity sensors."""
    first = dt_util.utcnow().replace(microsecond=0)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    mock_client.async_get_device_properties.assert_awaited_with(DSN)

    reg = er.async_get(hass)
    climate_id = _eid(hass, "climate", "climate")
    device = _entry(reg, climate_id).device_id
    assert device is not None
    # all entities belong to the same device
    for key in ("last_contact", "indoor_temperature", "error_code"):
        assert _entry(reg, _eid(hass, "sensor", key)).device_id == device

    assert _state(hass, "sensor", "last_contact") == first.isoformat()
    assert _state(hass, "sensor", "last_poll") is not None
    assert _state(hass, "sensor", "last_change") == STATE_UNKNOWN
    assert _float_state(hass, "sensor", "indoor_temperature") == 12.0
    assert _float_state(hass, "sensor", "outdoor_temperature_c") == 15.5
    assert _state(hass, "sensor", "error_code") == "0"
    # further properties are created disabled; placeholders and handled ones not at all
    assert _entry(reg, _eid(hass, "sensor", "model_name")).disabled_by is not None
    assert reg.async_get_entity_id("sensor", DOMAIN, f"{DSN}_monitor1") is None
    assert reg.async_get_entity_id("sensor", DOMAIN, f"{DSN}_fan_speed") is None

    # connectivity sensors (polled entities)
    for key in ("connectivity", "cloud_connection"):
        await async_update_entity(hass, _eid(hass, "binary_sensor", key))
        assert _state(hass, "binary_sensor", key) == STATE_ON
    climate_state = hass.states.get(climate_id)
    assert climate_state is not None
    assert climate_state.state != "unavailable"

    # second poll: a value changed -> "Last change", sensors written again
    freezer.tick(timedelta(minutes=2))
    second = dt_util.utcnow().replace(microsecond=0)
    payload[DSN] = _properties(_stamp(second), error_code=7)
    await async_update_entity(hass, climate_id)
    await hass.async_block_till_done()
    assert _state(hass, "sensor", "error_code") == "7"
    assert _state(hass, "sensor", "last_change") == second.isoformat()
    assert _state(hass, "sensor", "last_contact") == second.isoformat()

    # no new poll for too long: cloud connection off, unit unknown
    freezer.tick(STALE_AFTER + timedelta(minutes=1))
    await async_update_entity(hass, _eid(hass, "binary_sensor", "cloud_connection"))
    await async_update_entity(hass, _eid(hass, "binary_sensor", "connectivity"))
    assert _state(hass, "binary_sensor", "cloud_connection") == STATE_OFF
    assert _state(hass, "binary_sensor", "connectivity") == STATE_UNKNOWN

    assert await hass.config_entries.async_unload(config_entry.entry_id)


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_platforms_pick_up_known_devices(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
) -> None:
    """After a reload the platforms create their entities from the stored data."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert DSN in hass.data[DOMAIN]["properties"]
    # a repeated signal does not create entities twice
    name, properties, extras = hass.data[DOMAIN]["properties"][DSN]
    async_dispatcher_send(hass, SIGNAL_PROPERTIES, DSN, name, properties, extras)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert _state(hass, "sensor", "error_code") == "0"
    assert hass.states.get(_eid(hass, "binary_sensor", "connectivity")) is not None


# ---------------------------------------------------------------- helpers


def test_is_placeholder() -> None:
    """65535 (or only 65535/empty parts) means: not supported by this model."""
    assert is_placeholder(None) is True
    assert is_placeholder(True) is False
    assert is_placeholder(False) is False
    assert is_placeholder(65535) is True
    assert is_placeholder(65535.0) is True
    assert is_placeholder(0) is False
    assert is_placeholder("65535,65535:") is True
    assert is_placeholder("") is True
    assert is_placeholder("1,65535") is False


def test_names() -> None:
    """Translation keys and English fallback names of the property sensors."""
    assert translation_key("outdoor_temperature") == "outdoor_temperature_raw"
    assert translation_key("error_code") == "error_code"
    assert translation_key("something_else") is None
    assert display_name("error_code") == "Error code"
    assert display_name("_new_prop_") == "New prop"


def test_device_info() -> None:
    """Shared device of the climate entity and the sensors."""
    info = device_info(DSN, None)
    assert info["identifiers"] == {(DOMAIN, DSN)}
    assert info["name"] == DSN
    assert device_info(DSN, "Living Room")["name"] == "Living Room"


def test_climate_device_info(hass: HomeAssistant) -> None:
    """The climate entity uses the shared device, also without a known name."""
    entity = FujitsuClimate(
        fglair_api_client=MagicMock(),
        dsn=DSN,
        region="eu",
        tokenpath=DEFAULT_TOKEN_PATH,
        temperature_offset=DEFAULT_TEMPERATURE_OFFSET,
        hass=hass,
        coordinator=MagicMock(),
    )
    with patch.object(
        FujitsuClimate, "name", property(lambda _: (_ for _ in ()).throw(KeyError))
    ):
        assert entity.device_info["name"] == DSN
    with patch.object(FujitsuClimate, "name", "Living Room"):
        assert entity.device_info["name"] == "Living Room"


def test_outdoor_degree() -> None:
    """Raw outdoor temperature -> degrees C, None if not supported."""
    device = MagicMock()
    for raw in (None, {}, {"value": "abc"}, {"value": 65535}, {"value": 0}):
        device.get_outdoor_temperature.return_value = raw
        assert _outdoor_degree(device) is None
    device.get_outdoor_temperature.return_value = {"value": 4750}
    assert _outdoor_degree(device) == -2.5


# ---------------------------------------------------------------- manager


def _manager() -> tuple[_DiagnosticsManager, list[Entity]]:
    """Diagnostics manager collecting the created entities."""
    added: list[Entity] = []

    def add_entities(
        new_entities: Iterable[Entity], update_before_add: bool = False
    ) -> None:
        added.extend(new_entities)

    return _DiagnosticsManager(add_entities), added


def _by_key(entities: list[Entity]) -> dict[str, _BaseSensor]:
    """Return the created entities by unique id suffix."""
    sensors: dict[str, _BaseSensor] = {}
    for entity in entities:
        assert isinstance(entity, _BaseSensor)
        assert entity.unique_id is not None
        sensors[entity.unique_id.removeprefix(f"{DSN}_")] = entity
    return sensors


def _native(
    sensor: _BaseSensor,
) -> StateType | date | datetime | Decimal:
    """Read the current value anew (it changes with every update)."""
    return sensor.native_value


def test_manager_ignores_invalid_data() -> None:
    """No list or invalid items: nothing is created from them."""
    mgr, added = _manager()
    mgr.async_update(DSN, "Living Room", None)
    assert added == []
    mgr.async_update(
        DSN,
        "Living Room",
        ["garbage", {"property": "x"}, {"property": {"value": 1}}],
    )
    # only the fixed sensors of the device
    assert sorted(_by_key(added)) == [
        "indoor_temperature",
        "last_change",
        "last_contact",
        "last_poll",
    ]


def test_manager_last_change_and_outdoor() -> None:
    """Last change without timestamps; outdoor sensor kept once it exists."""
    mgr, added = _manager()
    item = {"property": {"name": "op_status", "value": 1}}
    mgr.async_update(DSN, "Living Room", [item], {"outdoor": 10.5})
    sensors = _by_key(added)
    assert _native(sensors["outdoor_temperature_c"]) == 10.5
    assert _native(sensors["last_change"]) is None

    # value changed, no data_updated_at: time of the poll
    before = dt_util.utcnow()
    item = {"property": {"name": "op_status", "value": 2}}
    mgr.async_update(DSN, "Living Room", [item], {"outdoor": None})
    last_change = _native(sensors["last_change"])
    assert isinstance(last_change, datetime)
    assert last_change >= before
    assert _native(sensors["outdoor_temperature_c"]) is None
    assert _native(sensors["op_status"]) == 2
    assert len(added) == len(sensors)


def test_manager_writes_active_sensors() -> None:
    """Sensors already active in Home Assistant are written on every poll."""
    mgr, added = _manager()
    item = {"property": {"name": "op_status", "value": 1}}
    mgr.async_update(DSN, "Living Room", [item])
    sensor = _by_key(added)["op_status"]
    sensor.active = True
    with patch.object(_PropertySensor, "async_write_ha_state") as write:
        mgr.async_update(DSN, "Living Room", [item])
        # another device: not written
        mgr.async_update("other", "Other", [item])
    write.assert_called_once()


# ---------------------------------------------------------------- sensors


def test_property_sensor_values() -> None:
    """Numbers stay numbers, other values become text, long text is shortened."""
    sensor = _PropertySensor(DSN, "Living Room", "error_code")
    assert sensor.icon == "mdi:alert-circle-outline"
    assert sensor.entity_registry_enabled_default is True
    sensor.set_value(5)
    assert sensor.native_value == 5
    sensor.set_value(True)
    assert sensor.native_value == "True"

    other = _PropertySensor(DSN, "Living Room", "custom_thing")
    assert other.name == "Custom thing"
    assert other.entity_registry_enabled_default is False
    other.set_value(LONG)
    shortened = other.native_value
    assert isinstance(shortened, str)
    assert len(shortened) == _MAX_STATE
    assert shortened.endswith("…")
    assert other.extra_state_attributes == {"value": LONG}


def test_temperature_sensor_values() -> None:
    """Only numbers are temperatures."""
    sensor = _TemperatureSensor(DSN, None, "indoor_temperature", "Indoor", None)
    sensor.set_value(21.5)
    assert sensor.native_value == 21.5
    sensor.set_value("21.5")
    assert sensor.native_value is None


def test_base_sensor_set_value() -> None:
    """Subclasses have to implement set_value."""
    with pytest.raises(NotImplementedError):
        _BaseSensor(DSN, None, "k", "Name").set_value(1)


# ---------------------------------------------------------------- binary sensors


async def test_connectivity_sensors(hass: HomeAssistant) -> None:
    """Cloud connection and connectivity from the stored poll status."""
    cloud = _CloudConnection(hass, DSN, "Living Room")
    unit = _DeviceConnectivity(hass, DSN, "Living Room")
    assert cloud.unique_id == f"{DSN}_cloud_connection"
    assert unit.unique_id == f"{DSN}_connectivity"

    async def update() -> tuple[bool | None, bool | None]:
        await cloud.async_update()
        await unit.async_update()
        return cloud.is_on, unit.is_on

    # nothing polled yet
    assert await update() == (False, None)

    now = dt_util.utcnow()
    status: dict[str, Any] = {"last_poll": now, "last_contact": now}
    hass.data.setdefault(DOMAIN, {})["status"] = {DSN: status}
    assert await update() == (True, True)

    # unit silent although the cloud answers
    status["last_contact"] = now - STALE_AFTER - timedelta(seconds=1)
    assert await update() == (True, False)
    status["last_contact"] = None
    assert await update() == (True, False)

    # no fresh poll: nothing known about the unit
    status["last_poll"] = now - STALE_AFTER - timedelta(seconds=1)
    assert await update() == (False, None)
