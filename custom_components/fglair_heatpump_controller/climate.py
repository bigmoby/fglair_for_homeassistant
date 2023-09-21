"""
Support for the Fujitsu General Split A/C Wifi platform AKA FGLair .
"""

import logging
from typing import Any, Final

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
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PASSWORD,
    CONF_USERNAME,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from pyfujitsugeneral.api import Api as fgapi
from pyfujitsugeneral.splitAC import SplitAC as splitAC


_LOGGER = logging.getLogger(__name__)

# Values from web interface
MIN_TEMP = 16
MAX_TEMP = 30
DEFAULT_TEMPERATURE_OFFSET: Final = 0.0
DEFAULT_MIN_STEP: Final = 0.5
DEFAULT_TOKEN_PATH = "token.txt"
DEFAULT_ALT_HEAT = False
VERTICAL = "vertical_"
SWING = "swing"

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
        vol.Optional("temperature_offset", default=DEFAULT_TEMPERATURE_OFFSET): vol.All(
            vol.Coerce(float), vol.Range(min=-5, max=5)
        ),
        vol.Optional("alt_heat", default=DEFAULT_ALT_HEAT): cv.boolean,
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

HA_STATE_TO_FUJITSU = {value: key for key, value in FUJITSU_TO_HA_STATE.items()}

SUPPORTED_MODES: list[HVACMode] = [
    HVACMode.OFF,
    HVACMode.HEAT,
    HVACMode.COOL,
    HVACMode.AUTO,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
]


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Setup the FujitsuClimate Platform."""

    _LOGGER.debug("FujitsuClimate setup_platform called")

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    region = config.get("region")
    tokenpath = config.get("tokenpath", DEFAULT_TOKEN_PATH)
    temperature_offset = config.get("temperature_offset", DEFAULT_TEMPERATURE_OFFSET)
    alt_heat = config.get("alt_heat")

    fglairapi = fgapi(username, password, region, tokenpath)

    if not fglairapi._authenticate():
        _LOGGER.error("Unable to authenticate with Fujistsu General")
        return

    devices = fglairapi.get_devices_dsn()
    add_entities(
        FujitsuClimate(fglairapi, dsn, region, temperature_offset, alt_heat)
        for dsn in devices
    )


class FujitsuClimate(ClimateEntity):
    """Representation of a Fujitsu HVAC device."""

    def __init__(
        self,
        api: fgapi,
        dsn: str,
        region: str,
        temperature_offset: float,
        alt_heat: bool,
    ) -> None:
        """Initialize the thermostat."""
        _LOGGER.debug("FujitsuClimate init called for dsn: %s", dsn)
        self._api = api
        self._dsn = dsn
        self._region = region
        self._temperature_offset = temperature_offset
        self._alt_heat = alt_heat
        self._fujitsu_device = splitAC(self._dsn, self._api)

        _LOGGER.debug("FujitsuClimate instantiate splitAC")
        self._name = self.name
        self._unique_id = self.unique_id
        self._aux_heat = self.is_aux_heat_on
        self._current_temperature = self.current_temperature
        self._target_temperature = self.target_temperature
        self._fan_mode = self.fan_mode
        self._hvac_mode = self.hvac_mode
        self._swing_mode = self.swing_mode
        self._swing_modes = self.swing_modes

        self._fan_modes: list[Any] = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
            FAN_DIFFUSE,
        ]
        self._hvac_modes: list[HVACMode] = SUPPORTED_MODES
        self._preset_modes: list[Any] = [PRESET_NONE, PRESET_ECO, PRESET_BOOST]
        self._on = self.is_on
        """_LOGGER.debug(
            "FujitsuClimate finish init for device [%s] properties [%s]",
            self.name,
            self._fujitsu_device._properties,
        )"""

    @property
    def name(self) -> str:
        """Return the name of the thermostat."""
        data: str = self._fujitsu_device.device_name["value"]
        _LOGGER.debug("FujitsuClimate return device name [%s]", data)
        return data

    @property
    def is_aux_heat_on(self) -> bool:
        """Reusing is for Powerfull mode."""
        if not hasattr(self._fujitsu_device.powerful_mode, "value"):
            return False
        elif self._fujitsu_device.powerful_mode["value"] == 1:
            return True
        else:
            return False

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature in degrees Celsius."""
        curtemp = self._fujitsu_device._get_prop_from_json(
            "display_temperature", self._fujitsu_device._properties
        )
        if not curtemp:
            return None
        else:
            if curtemp["value"] == 65535:
                _LOGGER.error("Display_temperature value not valid.")
                return None

            converted_display_temperature = round(
                ((curtemp["value"] / 100 - 32) * 5 / 9) + self._temperature_offset, 1
            )
            _LOGGER.debug(
                "FujitsuClimate device [%s] return display_temperature [%s]",
                self._name,
                converted_display_temperature,
            )
            return float(converted_display_temperature)

    def set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (target_temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            rounded_temperature = self.round_off_temperature(target_temperature)
            _LOGGER.debug(
                "FujitsuClimate device [%s] set_temperature [%s] will be rounded with [%s]",
                self._name,
                target_temperature,
                rounded_temperature,
            )
            self._fujitsu_device.changeTemperature(rounded_temperature)
        else:
            _LOGGER.error(
                "FujitsuClimate device [%s] A target temperature must be provided",
                self._name,
            )

    def round_off_temperature(self, temperature: float) -> float:
        """Round temperature to the closest half."""
        return round(temperature * 2) / 2

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        data: float = self._fujitsu_device.adjust_temperature_degree
        return data

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return DEFAULT_MIN_STEP

    @property
    def is_on(self) -> bool:
        """Return true if on."""
        if self._fujitsu_device.operation_mode["value"] != 0:
            return True
        else:
            return False

    @property
    def hvac_mode(self) -> Any:
        """Return current operation ie. heat, cool, idle."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] return current operation_mode [%s] ; operation_mode_desc [%s]",
            self._name,
            self._fujitsu_device.operation_mode["value"],
            self._fujitsu_device.operation_mode_desc,
        )
        return FUJITSU_TO_HA_STATE[self._fujitsu_device.operation_mode_desc]

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """HVAC modes."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] listing all supported hvac_modes [%s]",
            self._name,
            self._hvac_modes,
        )
        return self._hvac_modes

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] set_hvac_mode called. Current _hvac_mode [%s] ; new hvac_mode [%s]",
            self._name,
            self._hvac_mode,
            hvac_mode,
        )
        if hvac_mode not in HA_STATE_TO_FUJITSU:
            raise ValueError(
                f"FujitsuClimate device [{self._name}] Unsupported HVAC mode: {hvac_mode}"
            )

        if hvac_mode == HVACMode.OFF:
            """Turn device off."""
            self._fujitsu_device.turnOff()
        elif hvac_mode == HVACMode.HEAT and self._alt_heat:
            self._fujitsu_device.changeOperationMode("heat_alt")
        else:
            self._fujitsu_device.changeOperationMode(HA_STATE_TO_FUJITSU.get(hvac_mode))

        _LOGGER.debug(
            "FujitsuClimate device [%s] set_hvac_mode called. Current mode [%s] new will be [%s]",
            self._name,
            self._hvac_mode,
            hvac_mode,
        )

    def turn_on(self) -> None:
        """Set the HVAC State to on by setting the operation mode to the last operation mode other than off"""
        _LOGGER.debug("Turning on FujitsuClimate device [%s]", self._name)
        self._fujitsu_device.turnOn()

    def turn_off(self) -> None:
        """Set the HVAC State to off."""
        _LOGGER.debug("Turning off FujitsuClimate device [%s]", self._name)
        self._fujitsu_device.turnOff()

    def update(self) -> None:
        """Retrieve latest state."""
        _LOGGER.debug("Update FujitsuClimate device [%s]", self._name)
        self._fujitsu_device.refresh_properties()

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

    def set_fan_mode(self, fan_mode: Any) -> None:
        """Set fan mode."""
        new_fan_speed = DICT_FAN_MODE[fan_mode]
        _LOGGER.debug(
            "FujitsuClimate device [%s] set fan mode [%s], fan speed [%s]",
            self._name,
            fan_mode,
            new_fan_speed,
        )
        self._fujitsu_device.changeFanSpeed(new_fan_speed)

    @property
    def swing_mode(self) -> str:
        """Return the swing setting."""
        vaneVerticalValue = self._fujitsu_device.vane_vertical()
        swingVerticalValue = self._fujitsu_device.af_vertical_swing
        if swingVerticalValue == 1:
            mode = self.swing_modes[0]
        elif self._swing_modes[0] == VERTICAL + SWING:
            mode = self.swing_modes[vaneVerticalValue]
        else:
            mode = self.swing_modes[vaneVerticalValue-1]
        _LOGGER.debug(
            "FujitsuClimate device [%s] vane value [%s]",
            self._name,
            mode,
        )
        return mode

    @property
    def swing_modes(self) -> list[str]:
        """List of available swing modes."""
        # Currently only vertical modes supported
        pos_list: list[str] = self._fujitsu_device.vane_vertical_positions()

        # Add swing mode to start of list if supported
        modes_list = self._fujitsu_device.swing_modes()
        if modes_list in ["Vertical", "Both"]:
            pos_list = [SWING] + pos_list
        
        self._swing_modes = [VERTICAL + itm for itm in pos_list]
        _LOGGER.debug(
            "FujitsuClimate device [%s] returning swing modes [%s]",
            self._name,
            self._swing_modes,
        )
        return self._swing_modes

    def set_swing_mode(self, swing_mode: Any) -> None:
        """Set new target swing."""
        if swing_mode == VERTICAL + SWING:
            self._fujitsu_device.af_vertical_swing = 1
        else:
            self._fujitsu_device.set_vane_vertical_position(int(swing_mode[-1]))
        _LOGGER.debug(
            "FujitsuClimate device [%s] swing choice [%s]",
            self._name,
            swing_mode,
        )

    @property
    def preset_mode(self) -> Any:
        """Return the preset setting."""
        if not self._fujitsu_device._get_prop_from_json(
            "economy_mode", self._fujitsu_device._properties
        ) or not self._fujitsu_device._get_prop_from_json(
            "powerful_mode", self._fujitsu_device._properties
        ):
            _LOGGER.debug(
                "FujitsuClimate device [%s] has no preset props",
                self._name,
            )
            return PRESET_NONE
        else:
            if self._fujitsu_device.economy_mode["value"] == 1:
                _LOGGER.debug(
                    "FujitsuClimate device [%s] preset eco setting: %s",
                    self._name,
                    self._fujitsu_device.economy_mode["value"],
                )
                return PRESET_ECO
            if self._fujitsu_device.powerful_mode["value"] == 1:
                _LOGGER.debug(
                    "FujitsuClimate device [%s] preset boost setting: %s",
                    self._name,
                    self._fujitsu_device.powerful_mode["value"],
                )
                return PRESET_BOOST
            return PRESET_NONE

    @property
    def preset_modes(self) -> list[Any]:
        """List of available preset modes."""
        return self._preset_modes

    def set_preset_mode(self, preset_mode: Any) -> None:
        """Set preset mode."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] preset choice: %s",
            self._name,
            preset_mode.upper(),
        )
        if preset_mode == PRESET_NONE:
            self._fujitsu_device.economy_mode = 0
            self._fujitsu_device.powerful_mode = 0
        elif preset_mode == PRESET_ECO:
            self._fujitsu_device.economy_mode = 1
        elif preset_mode == PRESET_BOOST:
            self._fujitsu_device.powerful_mode = 1

    ############ old stuff

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
