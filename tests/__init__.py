"""Tests for fglair_heatpump_controller integration."""

from custom_components.fglair_heatpump_controller.climate import FujitsuClimate
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def setup_integration(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Fixture for setting up the component."""
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


def entity_id(device: FujitsuClimate) -> str:
    """Generate the entity id for the given serial."""
    return f"{Platform.CLIMATE}.{device.unique_id}"
