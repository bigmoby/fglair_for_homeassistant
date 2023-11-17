"""Support for the Fujitsu General Split A/C Wifi platform AKA FGLair ."""

import logging
from datetime import datetime
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_DIFFUSE,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_NONE,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_VERTICAL,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PASSWORD,
    CONF_REGION,
    CONF_USERNAME,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import Throttle
from homeassistant.util.dt import utcnow
from pyfujitsugeneral.client import FGLairApiClient
from pyfujitsugeneral.splitac import SplitAC, get_prop_from_json

from . import FglairDataUpdateCoordinator
from .const import (
    CONF_TEMPERATURE_OFFSET,
    CONF_TOKENPATH,
    DEFAULT_MIN_STEP,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    HORIZONTAL,
    MAX_TEMP,
    MIN_TEMP,
    MIN_TIME_BETWEEN_UPDATES,
    REFRESH_MINUTES_INTERVAL,
    VERTICAL,
)

_LOGGER = logging.getLogger(__name__)


SUPPORT_FLAGS: Any = (
    SUPPORT_FAN_MODE
    | SUPPORT_SWING_MODE
    | SUPPORT_TARGET_TEMPERATURE
    | SUPPORT_PRESET_MODE
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional("region"): cv.string,
        vol.Optional("tokenpath", default=DEFAULT_TOKEN_PATH): cv.string,
        vol.Optional(
            "temperature_offset", default=DEFAULT_TEMPERATURE_OFFSET
        ): vol.All(vol.Coerce(float), vol.Range(min=-5, max=5)),
    }
)

DICT_FAN_MODE = {
    FAN_AUTO: "Auto",
    FAN_LOW: "Low",
    FAN_MEDIUM: "Medium",
    FAN_HIGH: "High",
    FAN_DIFFUSE: "Quiet",
    "Auto": FAN_AUTO,
    "Low": FAN_LOW,
    "Medium": FAN_MEDIUM,
    "High": FAN_HIGH,
    "Quiet": FAN_DIFFUSE,
}

FUJITSU_TO_HA_STATE = {
    "off": HVACMode.OFF,
    "auto": HVACMode.AUTO,
    "cool": HVACMode.COOL,
    "dry": HVACMode.DRY,
    "fan_only": HVACMode.FAN_ONLY,
    "heat": HVACMode.HEAT,
}

HA_STATE_TO_FUJITSU = {
    value: key for key, value in FUJITSU_TO_HA_STATE.items()
}

SUPPORTED_MODES: list[HVACMode] = [
    HVACMode.OFF,
    HVACMode.HEAT,
    HVACMode.COOL,
    HVACMode.AUTO,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setups the FujitsuClimate Platform based on a config entry."""
    _LOGGER.debug("FujitsuClimate async_setup_entry called")

    coordinator: FglairDataUpdateCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]

    username: str = entry.data[CONF_USERNAME]
    password: str = entry.data[CONF_PASSWORD]
    region: str = entry.data[CONF_REGION]
    tokenpath: str = entry.data[CONF_TOKENPATH]
    temperature_offset: float = entry.data[CONF_TEMPERATURE_OFFSET]

    fglair_api_client: FGLairApiClient = FGLairApiClient(
        username, password, region, tokenpath, async_get_clientsession(hass)
    )

    auth_result = await fglair_api_client.async_authenticate()

    if not auth_result:
        _LOGGER.error("Unable to authenticate with Fujistsu General")
        return

    devices = await fglair_api_client.async_get_devices_dsn()

    entities = []

    for dsn in devices:
        _LOGGER.debug(
            "async_setup_entry called with %s - %s - %s - %s  ",
            dsn,
            region,
            tokenpath,
            temperature_offset,
        )
        entities.append(
            FujitsuClimate(
                fglair_api_client,
                dsn,
                region,
                tokenpath,
                temperature_offset,
                hass,
                coordinator,
            )
        )

    async_add_entities(entities, update_before_add=True)


class FujitsuClimate(
    CoordinatorEntity[FglairDataUpdateCoordinator], ClimateEntity
):  # pylint: disable=R0902,R0904,R0913
    """Representation of a Fujitsu HVAC device."""

    def __init__(
        self,
        fglair_api_client: FGLairApiClient,
        dsn: str,
        region: str,
        tokenpath: str,
        temperature_offset: float,
        hass: HomeAssistant,
        coordinator: FglairDataUpdateCoordinator,
    ) -> None:  # pylint: disable=R0913
        """Initialize the thermostat."""
        _LOGGER.debug("FujitsuClimate init called for dsn: %s", dsn)
        super().__init__(coordinator)
        self._fglairapi_client = fglair_api_client
        self._dsn = dsn
        self._region = region
        self._temperature_offset = temperature_offset
        self._tokenpath = tokenpath
        self._hass = hass
        self._fujitsu_device = SplitAC(
            self._dsn, self._fglairapi_client, tokenpath, temperature_offset
        )
        self._properties = None
        self._name = ""
        self._unique_id: str = ""
        self._aux_heat: bool = False
        self._current_temperature: float | None = None
        self._target_temperature: float | None = None
        self._fan_mode = None
        self._hvac_mode = None
        self._swing_modes: list[str] | None = None
        self._swing_mode: str = ""
        self._fan_modes: list[Any] = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
            FAN_DIFFUSE,
        ]
        self._hvac_modes: list[HVACMode] = SUPPORTED_MODES
        self._preset_modes: list[Any] = [PRESET_NONE, PRESET_ECO, PRESET_BOOST]
        self._on: bool | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update attributes when the coordinator updates."""
        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @property
    def name(self) -> str:
        """Return the name of the thermostat."""
        data: str = self._fujitsu_device.get_device_name()["value"]
        _LOGGER.debug("FujitsuClimate return device name [%s]", data)
        return data

    @property
    def is_aux_heat_on(self) -> bool:
        """Reusing is for Powerfull mode."""
        if not hasattr(self._fujitsu_device.get_powerful_mode(), "value"):
            return False

        if self._fujitsu_device.get_powerful_mode()["value"]:
            return True

        return False

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature in degrees Celsius."""
        return self._current_temperature

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (target_temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            rounded_temperature = self.round_off_temperature(
                target_temperature
            )
            _LOGGER.debug(
                "FujitsuClimate device [%s] set_temperature [%s] will be"
                " rounded with [%s]",
                self._name,
                target_temperature,
                rounded_temperature,
            )
            await self._fujitsu_device.async_change_temperature(
                rounded_temperature
            )
        else:
            _LOGGER.error(
                "FujitsuClimate device [%s] A target temperature must be"
                " provided",
                self._name,
            )

    def round_off_temperature(self, temperature: float) -> float:
        """Round temperature to the closest half."""
        return round(temperature * 2) / 2

    async def async_target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        data = await self._fujitsu_device.async_get_adjust_temperature_degree()
        return data

    @property
    def target_temperature(self) -> float | None:
        """Getter for the temperature we try to reach."""
        return self._target_temperature

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return DEFAULT_MIN_STEP

    @property
    def is_on(self) -> bool:
        """Return true if on."""
        if self._fujitsu_device.get_operation_mode()["value"] != 0:
            return True
        return False

    @property
    def hvac_mode(self) -> Any:
        """Return current operation ie. heat, cool, idle."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] return current operation_mode [%s] ;"
            " operation_mode_desc [%s]",
            self._name,
            self._fujitsu_device.get_operation_mode()["value"],
            self._fujitsu_device.get_operation_mode_desc(),
        )
        return FUJITSU_TO_HA_STATE[
            self._fujitsu_device.get_operation_mode_desc()
        ]

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """HVAC modes."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] listing all supported hvac_modes [%s]",
            self._name,
            self._hvac_modes,
        )
        return self._hvac_modes

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] set_hvac_mode called. Current"
            " _hvac_mode [%s] ; new hvac_mode [%s]",
            self._name,
            self._hvac_mode,
            hvac_mode,
        )
        if hvac_mode not in HA_STATE_TO_FUJITSU:
            raise ValueError(
                f"FujitsuClimate device [{self._name}] Unsupported HVAC mode:"
                f" {hvac_mode}"
            )

        if hvac_mode == HVACMode.OFF:
            await self._fujitsu_device.async_turnOff()
        else:
            await self._fujitsu_device.async_change_operation_mode(
                HA_STATE_TO_FUJITSU.get(hvac_mode)
            )

        _LOGGER.debug(
            "FujitsuClimate device [%s] set_hvac_mode called. Current mode"
            " [%s] new will be [%s]",
            self._name,
            self._hvac_mode,
            hvac_mode,
        )

    async def async_turn_on(self) -> None:
        """Set the HVAC State to on."""
        _LOGGER.debug("Turning on FujitsuClimate device [%s]", self._name)
        await self._fujitsu_device.async_turnOn()

    async def async_turn_off(self) -> None:
        """Set the HVAC State to off."""
        _LOGGER.debug("Turning off FujitsuClimate device [%s]", self._name)
        await self._fujitsu_device.async_turnOff()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Retrieve latest state."""
        _LOGGER.debug("Update FujitsuClimate device by async_update")
        self._properties = await self._fujitsu_device.async_update_properties()
        self._name = self.name
        self._unique_id = self.unique_id
        self._aux_heat = self.is_aux_heat_on
        self._current_temperature = (
            await self._fujitsu_device.async_get_display_temperature_degree()
        )
        await self._async_refresh_display_temperature_request(
            self._fujitsu_device.get_refresh()["data_updated_at"]
        )
        self._target_temperature = await self.async_target_temperature()
        self._fan_mode = self.fan_mode
        self._hvac_mode = self.hvac_mode
        self._swing_modes = self.swing_modes
        self._swing_mode = self.swing_mode
        self._fan_modes = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
            FAN_DIFFUSE,
        ]
        self._hvac_modes = SUPPORTED_MODES
        self._preset_modes = [PRESET_NONE, PRESET_ECO, PRESET_BOOST]
        self._on = self.is_on
        _LOGGER.debug(
            "FujitsuClimate finish async_update for device [%s]",
            self.name,
        )

    async def _async_refresh_display_temperature_request(
        self, refreshed_data_updated_at_str: str
    ) -> None:
        refreshed_data_updated_at = datetime.strptime(
            refreshed_data_updated_at_str, "%Y-%m-%dT%H:%M:%S%z"
        )
        _LOGGER.debug(
            "Last refreshed update date [%s]", refreshed_data_updated_at
        )
        must_be_refreshed = utcnow() > (
            refreshed_data_updated_at + REFRESH_MINUTES_INTERVAL
        )

        if must_be_refreshed:
            _LOGGER.debug(
                "display_temperature will be refreshed in async mode"
            )
            await self._fujitsu_device.async_set_refresh(1)

    @property
    def fan_mode(self) -> Any:
        """Return the fan setting."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] return fan_mode [%s]",
            self._name,
            DICT_FAN_MODE[self._fujitsu_device.get_fan_speed_desc()],
        )
        return DICT_FAN_MODE[self._fujitsu_device.get_fan_speed_desc()]

    @property
    def fan_modes(self) -> list[Any]:
        """Return the list of available fan modes."""
        return self._fan_modes

    async def async_set_fan_mode(self, fan_mode: Any) -> None:
        """Set new target fan mode."""
        new_fan_speed = DICT_FAN_MODE[fan_mode]
        _LOGGER.debug(
            "FujitsuClimate device [%s] set fan mode [%s], fan speed [%s]",
            self._name,
            fan_mode,
            new_fan_speed,
        )
        await self._fujitsu_device.async_changeFanSpeed(new_fan_speed)

    @property
    def swing_mode(self) -> str:
        """Return the swing setting."""
        # Not only returns vertical settings,
        # horizontal setting except for swing ignored
        vane_vertical_value = self._fujitsu_device.vane_vertical()
        swing_vertical = self._fujitsu_device.get_af_vertical_swing()["value"]
        swing_horizontal = self._fujitsu_device.get_af_horizontal_swing()[
            "value"
        ]

        _LOGGER.debug(
            "FujitsuClimate device [%s] swing value %s",
            self._name,
            swing_vertical,
        )
        if swing_vertical and swing_horizontal:
            mode = SWING_BOTH
        elif swing_vertical:
            mode = SWING_VERTICAL
        else:
            mode = VERTICAL + str(vane_vertical_value)

        self._swing_mode = mode

        _LOGGER.debug(
            "FujitsuClimate device [%s] mode value [%s]",
            self._name,
            mode,
        )
        _LOGGER.debug(
            "FujitsuClimate device [%s] vertical swing value [%s]",
            self._name,
            swing_vertical,
        )
        _LOGGER.debug(
            "FujitsuClimate device [%s] horizontal swing value [%s]",
            self._name,
            swing_horizontal,
        )
        return self._swing_mode

    @property
    def swing_modes(self) -> list[str] | None:
        """List of available swing modes."""

        vert_pos_list: list[str] = (
            self._fujitsu_device.vane_vertical_positions()
        )
        hori_pos_list: list[str] = (
            self._fujitsu_device.vane_horizontal_positions()
        )
        pos_list: list[str] | None = []

        # Add swing modes to start of list if supported
        modes_list = self._fujitsu_device.get_swing_modes_supported()
        if modes_list == "Both" and pos_list is not None:
            pos_list.append(SWING_VERTICAL)
            pos_list.append(SWING_HORIZONTAL)
            pos_list.append(SWING_BOTH)
            pos_list = pos_list + [
                VERTICAL + str(itm) for itm in vert_pos_list
            ]
            pos_list = pos_list + [
                HORIZONTAL + str(itm) for itm in hori_pos_list
            ]
        elif modes_list == "Vertical" and pos_list is not None:
            pos_list.append(SWING_VERTICAL)
            pos_list = pos_list + [
                VERTICAL + str(itm) for itm in vert_pos_list
            ]
        elif modes_list == "Horizontal" and pos_list is not None:
            pos_list.append(SWING_HORIZONTAL)
            pos_list = pos_list + [
                HORIZONTAL + str(itm) for itm in hori_pos_list
            ]
        else:
            pos_list = None

        self._swing_modes = pos_list
        _LOGGER.debug(
            "FujitsuClimate device [%s] returning swing modes [%s]",
            self._name,
            self._swing_modes,
        )
        return self._swing_modes

    async def async_set_swing_mode(self, swing_mode: Any) -> None:
        """Set new target swing."""
        # Note setting one direction will not affect other, except swing both
        if swing_mode == SWING_VERTICAL:
            await self._fujitsu_device.async_set_af_vertical_swing(1)
        elif swing_mode == SWING_HORIZONTAL:
            await self._fujitsu_device.async_set_af_horizontal_swing(1)
        elif swing_mode == SWING_BOTH:
            await self._fujitsu_device.async_set_af_vertical_swing(1)
            await self._fujitsu_device.async_set_af_horizontal_swing(1)
        elif swing_mode[0:9] == VERTICAL:
            await self._fujitsu_device.async_set_vane_vertical_position(
                int(swing_mode[-1])
            )
        elif swing_mode[0:11] == HORIZONTAL:
            await self._fujitsu_device.async_set_vane_horizontal_position(
                int(swing_mode[-1])
            )
        _LOGGER.debug(
            "FujitsuClimate device [%s] swing choice [%s]",
            self._name,
            swing_mode,
        )

    @property
    def preset_mode(self) -> Any:
        """Return the preset setting."""
        if not get_prop_from_json(
            "economy_mode", self._fujitsu_device.get_properties()
        ) or not get_prop_from_json(
            "powerful_mode", self._fujitsu_device.get_properties()
        ):
            _LOGGER.debug(
                "FujitsuClimate device [%s] has no preset props",
                self._name,
            )
            return PRESET_NONE

        if self._fujitsu_device.get_economy_mode()["value"]:
            _LOGGER.debug(
                "FujitsuClimate device [%s] preset eco setting: %s",
                self._name,
                self._fujitsu_device.get_economy_mode()["value"],
            )
            return PRESET_ECO
        if self._fujitsu_device.get_powerful_mode()["value"]:
            _LOGGER.debug(
                "FujitsuClimate device [%s] preset boost setting: %s",
                self._name,
                self._fujitsu_device.get_powerful_mode()["value"],
            )
            return PRESET_BOOST

        return PRESET_NONE

    @property
    def preset_modes(self) -> list[Any]:
        """List of available preset modes."""
        return self._preset_modes

    async def async_set_preset_mode(self, preset_mode: Any) -> None:
        """Set preset mode."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] preset choice: %s",
            self._name,
            preset_mode.upper(),
        )
        if preset_mode == PRESET_NONE:
            await self._fujitsu_device.async_set_economy_mode(0)
            await self._fujitsu_device.async_set_powerful_mode(0)
        elif preset_mode == PRESET_ECO:
            await self._fujitsu_device.async_set_economy_mode(1)
        elif preset_mode == PRESET_BOOST:
            await self._fujitsu_device.async_set_powerful_mode(1)

    # ===> old stuff

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this thermostat."""
        return "_".join([self._name, "climate"])

    @property
    def should_poll(self) -> bool:
        """Polling is required."""
        return True

    @property
    def min_temp(self) -> int:
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self) -> int:
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def temperature_unit(self) -> Any:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def supported_features(self) -> Any:
        """Return the list of supported features."""
        return SUPPORT_FLAGS
