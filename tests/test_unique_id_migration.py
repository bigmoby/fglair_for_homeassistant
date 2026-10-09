"""Integration tests for the legacy unique ID to DSN migration."""

from collections.abc import Iterator
from datetime import timedelta
from functools import partial
import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pyfujitsugeneral.exceptions import FGLairGeneralException
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.fglair_heatpump_controller import climate
from custom_components.fglair_heatpump_controller.const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DOMAIN,
)

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")

DSN_1 = "AC000W000000001"
DSN_2 = "AC000W000000002"


def _properties(name: str | None) -> list[dict[str, Any]]:
    """Return a minimal FGLair properties payload for a device."""
    props: dict[str, Any] = {
        "operation_mode": 0,
        "adjust_temperature": 220,
        "display_temperature": 6200,
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
    }
    if name is not None:
        props["device_name"] = name
    payload = [
        {"property": {"name": prop_name, "value": value, "key": index}}
        for index, (prop_name, value) in enumerate(props.items())
    ]
    payload.append(
        {
            "property": {
                "name": "refresh",
                "value": 0,
                "key": len(payload),
                "data_updated_at": dt_util.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        }
    )
    return payload


@pytest.fixture  # type: ignore[misc]
def device_names() -> dict[str, str | None]:
    """Device names reported by the FGLair API, keyed by DSN."""
    return {DSN_1: "Living Room"}


@pytest.fixture  # type: ignore[misc]
def mock_client(
    device_names: dict[str, str | None],
) -> Iterator[MagicMock]:
    """Patch the FGLair API client used by the integration."""
    client = MagicMock()
    client.async_authenticate = AsyncMock(return_value="token")
    client.async_get_devices_dsn = AsyncMock(side_effect=lambda: list(device_names))
    client.async_get_device_properties = AsyncMock(
        side_effect=lambda dsn: _properties(device_names[dsn])
    )
    with (
        patch(
            "custom_components.fglair_heatpump_controller.FGLairApiClient",
            return_value=client,
        ),
        patch(
            "custom_components.fglair_heatpump_controller.climate.FGLairApiClient",
            return_value=client,
        ),
        patch.object(
            climate,
            "_async_retry_api_call",
            partial(climate._async_retry_api_call, delay=0),
        ),
    ):
        yield client


@pytest.fixture  # type: ignore[misc]
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a config entry added to hass."""
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


def _register(
    entity_registry: er.EntityRegistry,
    unique_id: str,
    object_id: str,
    config_entry: MockConfigEntry | None,
) -> str:
    """Pre-register a climate entity and return its entity ID."""
    entity_id: str = entity_registry.async_get_or_create(
        CLIMATE_DOMAIN,
        DOMAIN,
        unique_id,
        suggested_object_id=object_id,
        config_entry=config_entry,
    ).entity_id
    return entity_id


def _climate_entries(
    entity_registry: er.EntityRegistry, config_entry: MockConfigEntry
) -> dict[str, str]:
    """Return the climate registry entries of a config entry by unique ID."""
    return {
        entry.unique_id: entry.entity_id
        for entry in er.async_entries_for_config_entry(
            entity_registry, config_entry.entry_id
        )
        if entry.domain == CLIMATE_DOMAIN
    }


async def _setup(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Set up the integration."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED


@pytest.mark.usefixtures("mock_client")  # type: ignore[misc]
async def test_new_install_uses_dsn_unique_id(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
) -> None:
    """Test a fresh install registers the entity with the DSN unique ID."""
    await _setup(hass, config_entry)

    assert _climate_entries(entity_registry, config_entry) == {
        f"{DSN_1}_climate": "climate.living_room"
    }
    assert hass.states.get("climate.living_room") is not None


async def test_legacy_unique_id_is_migrated(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
) -> None:
    """Test the legacy entity keeps its entity ID and gets the DSN unique ID."""
    entity_id = _register(
        entity_registry, "Living Room_climate", "living_room", config_entry
    )

    await _setup(hass, config_entry)

    assert _climate_entries(entity_registry, config_entry) == {
        f"{DSN_1}_climate": entity_id
    }
    assert hass.states.get(entity_id) is not None


async def test_no_extra_api_calls_without_legacy_entities(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
) -> None:
    """Test the migration does not hit the API once entities use the DSN."""
    _register(entity_registry, f"{DSN_1}_climate", "living_room", config_entry)

    await _setup(hass, config_entry)

    # Only the entity's own update_before_add reads the device properties
    mock_client.async_get_device_properties.assert_awaited_once_with(DSN_1)


async def test_renamed_device_keeps_its_entity(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
    device_names: dict[str, str | None],
) -> None:
    """Test renaming the device in FGLair no longer creates a new entity."""
    await _setup(hass, config_entry)

    device_names[DSN_1] = "Bedroom"
    assert await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert _climate_entries(entity_registry, config_entry) == {
        f"{DSN_1}_climate": "climate.living_room"
    }


async def test_api_failure_defers_setup_without_orphans(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
) -> None:
    """Test an API failure retries the platform instead of orphaning entities."""
    entity_id = _register(
        entity_registry, "Living Room_climate", "living_room", config_entry
    )
    mock_client.async_get_device_properties.side_effect = FGLairGeneralException(
        "API down"
    )

    await _setup(hass, config_entry)

    # Nothing registered next to the legacy entity, which is left untouched
    assert _climate_entries(entity_registry, config_entry) == {
        "Living Room_climate": entity_id
    }
    assert hass.states.get(entity_id) is None

    # The API recovers: the platform retries and completes the migration
    mock_client.async_get_device_properties.side_effect = lambda dsn: _properties(
        "Living Room"
    )
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=5))
    await hass.async_block_till_done()

    assert _climate_entries(entity_registry, config_entry) == {
        f"{DSN_1}_climate": entity_id
    }
    assert hass.states.get(entity_id) is not None


async def test_existing_stable_unique_id_is_not_overwritten(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a collision keeps both entries and warns the user."""
    legacy_entity_id = _register(
        entity_registry, "Living Room_climate", "living_room", config_entry
    )
    stable_entity_id = _register(
        entity_registry, f"{DSN_1}_climate", "living_room_dsn", config_entry
    )

    with caplog.at_level(logging.WARNING):
        await _setup(hass, config_entry)

    assert _climate_entries(entity_registry, config_entry) == {
        "Living Room_climate": legacy_entity_id,
        f"{DSN_1}_climate": stable_entity_id,
    }
    assert hass.states.get(stable_entity_id) is not None
    assert f"Remove [{legacy_entity_id}] manually" in caplog.text


@pytest.mark.parametrize(  # type: ignore[misc]
    "device_names", [{DSN_1: "Living Room", DSN_2: "Living Room"}]
)
async def test_duplicate_legacy_names_migrate_only_once(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
) -> None:
    """Test two devices sharing the legacy name do not steal the same entity."""
    entity_id = _register(
        entity_registry, "Living Room_climate", "living_room", config_entry
    )

    await _setup(hass, config_entry)

    entries = _climate_entries(entity_registry, config_entry)
    assert entries[f"{DSN_1}_climate"] == entity_id
    assert f"{DSN_2}_climate" in entries
    assert entries[f"{DSN_2}_climate"] != entity_id
    assert "Living Room_climate" not in entries


async def test_device_without_name_is_skipped(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    mock_client: MagicMock,
    device_names: dict[str, str | None],
) -> None:
    """Test a device without a reported name does not break the migration."""
    entity_id = _register(
        entity_registry, "Living Room_climate", "living_room", config_entry
    )
    device_names[DSN_1] = None

    await _setup(hass, config_entry)

    assert _climate_entries(entity_registry, config_entry) == {
        "Living Room_climate": entity_id
    }


@pytest.mark.usefixtures("mock_client")  # type: ignore[misc]
async def test_other_config_entry_entities_are_not_touched(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
) -> None:
    """Test entities of another FGLair account with the same name are kept."""
    other_entry = MockConfigEntry(domain=DOMAIN, unique_id="other@example.com")
    other_entry.add_to_hass(hass)
    other_entity_id = _register(
        entity_registry, "Living Room_climate", "other_living_room", other_entry
    )

    await _setup(hass, config_entry)

    assert entity_registry.async_get(other_entity_id).unique_id == (
        "Living Room_climate"
    )
    assert _climate_entries(entity_registry, config_entry) == {
        f"{DSN_1}_climate": "climate.living_room"
    }
