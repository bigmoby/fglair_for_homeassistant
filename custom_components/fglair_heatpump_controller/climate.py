"""
Support for the Fujitsu General Split A/C Wifi platform AKA FGLair .
"""

from typing import Final

import logging
import voluptuous as vol

from pyfujitseu.api import Api as fgapi
from pyfujitseu.splitAC import splitAC

from homeassistant.components.climate import (
    ClimateEntity, 
    PLATFORM_SCHEMA
)
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY,
    SUPPORT_FAN_MODE, SUPPORT_SWING_MODE, SUPPORT_AUX_HEAT, SUPPORT_TARGET_TEMPERATURE, SUPPORT_PRESET_MODE,
    FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_DIFFUSE,
    SWING_OFF, SWING_ON, SWING_VERTICAL, SWING_HORIZONTAL, SWING_BOTH,
    PRESET_NONE, PRESET_ECO, PRESET_BOOST,
    CURRENT_HVAC_HEAT, CURRENT_HVAC_IDLE)
from homeassistant.const import (
    ATTR_TEMPERATURE, 
    CONF_USERNAME, 
    CONF_PASSWORD, 
    UnitOfTemperature
)
import homeassistant.helpers.config_validation as cv

__version__ = '0.1.0'

_LOGGER = logging.getLogger(__name__)
# _LOGGER.setLevel(logging.DEBUG)

# REQUIREMENTS = ['pyfujitseu==0.9.3.2']

# Values from web interface
MIN_TEMP = 16
MAX_TEMP = 30
DEFAULT_TEMPERATURE_OFFSET: Final  = 0.0
DEFAULT_MIN_STEP: Final = 1.0

SUPPORT_FLAGS = SUPPORT_FAN_MODE | SUPPORT_SWING_MODE | SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE | SUPPORT_AUX_HEAT

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional('region'): cv.string,
    vol.Optional('tokenpath'): cv.string,
    vol.Optional(
        'temperature_offset', 
        default=DEFAULT_TEMPERATURE_OFFSET
    ): vol.All(
        vol.Coerce(float), 
        vol.Range(min=-5, max=5)
    ),
})

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
    "Quiet": FAN_DIFFUSE
}

def setup_platform(hass, config, add_entities, discovery_info = None):
    """Setup the E-Thermostaat Platform."""

    _LOGGER.debug("FujitsuClimate setup_platform called")

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    region = config.get('region')
    tokenpath = config.get('tokenpath')
    temperature_offset = config.get('temperature_offset', DEFAULT_TEMPERATURE_OFFSET)
    _LOGGER.debug("FujitsuClimate config.get ")

    fglairapi = fgapi(username, password, region, tokenpath)

    if not fglairapi._authenticate():
        _LOGGER.error("Unable to authenticate with Fujistsu General")
        return

    _LOGGER.debug("FujitsuClimate fglairapi._authenticate ")

    devices = fglairapi.get_devices_dsn()
    add_entities(FujitsuClimate(fglairapi, dsn, region, temperature_offset) for dsn in devices)
    _LOGGER.debug("FujitsuClimate setup_platform fine")


class FujitsuClimate(ClimateEntity):
    """Representation of a E-Thermostaat device."""

    def __init__(self, api, dsn, region, temperature_offset):
        """Initialize the thermostat."""
        _LOGGER.debug("FujitsuClimate init called for dsn: %s", dsn)
        _LOGGER.debug("FujitsuClimate pyfujitseu.splitAC called")
        self._api = api
        self._dsn = dsn
        self._region = region
        self._temperature_offset = temperature_offset
        self._fujitsu_device = splitAC(self._dsn, self._api)
        _LOGGER.debug("FujitsuClimate _fujitsu_device setup.")
        self._name = self.name
        _LOGGER.debug("FujitsuClimate name set: %s", self._name)
        self._aux_heat = self.is_aux_heat
        self._current_temperature = self.current_temperature
        self._target_temperature = self.target_temperature
        self._fan_mode = self.fan_mode
        self._hvac_mode = self.hvac_mode
        self._swing_mode = self.swing_mode

        self._fan_modes = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_DIFFUSE]
        self._hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY, HVAC_MODE_OFF]
        self._swing_modes = [SWING_OFF, SWING_ON, SWING_VERTICAL, SWING_HORIZONTAL]
        self._preset_modes = [PRESET_NONE, PRESET_ECO, PRESET_BOOST]
        self._on = self.is_on

        _LOGGER.debug("FujitsuClimate init fine.")
        _LOGGER.debug("FujitsuClimate name set: %s", self._fujitsu_device._properties )

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._fujitsu_device.device_name['value']

    @property
    def is_aux_heat(self):
        """Reusing is for Powerfull mode."""
        if self._fujitsu_device.powerful_mode['value'] == 1:
            return True
        else:
            return False
      
    def turn_aux_heat_on(self):
        """Turn auxiliary heater on."""
        self._fujitsu_device.powerful_mode = 1
    
    def turn_aux_heat_off(self):
        """Turn auxiliary heater off."""        
        self._fujitsu_device.powerful_mode = 0

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature in degrees Celsius."""
        curtemp = self._fujitsu_device._get_prop_from_json('display_temperature', self._fujitsu_device._properties)
        _LOGGER.debug("Display_temperature json: %s", curtemp)
        _LOGGER.debug("Display_temperature: %s", curtemp['value'])
        _LOGGER.debug("Region: %s", self._region)
        if curtemp['value'] == 65535 :
            return None
        return round(((curtemp['value'] / 100 - 32) * 5/9) + self._temperature_offset, 1)

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._fujitsu_device.adjust_temperature_degree

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return DEFAULT_MIN_STEP

    @property
    def is_on(self):
        """Return true if on."""
        if self._fujitsu_device.operation_mode['value'] != 0:
            return True
        else:
            return False

    @property
    def hvac_mode(self) -> str | None:
        """Return current operation ie. heat, cool, idle."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate hvac_mode: %s", self._fujitsu_device.operation_mode['value'])
        return self._fujitsu_device.operation_mode_desc

    @property
    def hvac_modes(self):
        """HVAC modes."""
        return self._hvac_modes

    def set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate set_hvac_mode called. self._hvac_mode: %s ; hvac_mode: %s", self._hvac_mode,
                      hvac_mode)
        if (hvac_mode == HVAC_MODE_OFF):
            """Turn device off."""
            self._fujitsu_device.turnOff()
        elif (self._hvac_mode != hvac_mode):
            _LOGGER.debug("FujitsuClimate set_hvac_mode elif path called. ")
            self._fujitsu_device.changeOperationMode(hvac_mode)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate set_temperature: %s ; 2: %s", kwargs.get(ATTR_TEMPERATURE),
                      kwargs.get(ATTR_TEMPERATURE))
        self._fujitsu_device.changeTemperature(kwargs.get(ATTR_TEMPERATURE))

    def update(self):
        """Retrieve latest state."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("Update FujitsuClimate", self._fujitsu_device.refresh_properties())
        self._fujitsu_device.refresh_properties()

    @property
    def fan_mode(self):
        """Return the fan setting."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate fan_mode: %s", DICT_FAN_MODE[self._fujitsu_device.get_fan_speed_desc()])
        return DICT_FAN_MODE[self._fujitsu_device.get_fan_speed_desc()]

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return self._fan_modes

    def set_fan_mode(self, fan_mode):
        """Set fan mode."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate fan modes: %s", self._fujitsu_device.changeFanSpeed(DICT_FAN_MODE[fan_mode]))
        self._fujitsu_device.changeFanSpeed(DICT_FAN_MODE[fan_mode])

    @property
    def swing_mode(self):
        """Return the swing setting."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate swing vertical settings: %s", self._fujitsu_device.af_vertical_swing['value'])
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate swing horizontal settings: %s", self._fujitsu_device.af_horizontal_swing['value'])

        if self._fujitsu_device.af_vertical_swing['value'] == 1 and self._fujitsu_device.af_horizontal_swing['value'] == 1:
            return 'on'
        elif self._fujitsu_device.af_vertical_swing['value'] == 1 and self._fujitsu_device.af_horizontal_swing['value'] == 0:
            return 'vertical'
        elif self._fujitsu_device.af_vertical_swing['value'] == 0 and self._fujitsu_device.af_horizontal_swing['value'] == 1:
            return 'horizontal'
        else:
            return 'off'

    @property
    def swing_modes(self):
        """List of available swing modes."""
        return self._swing_modes

    def set_swing_mode(self, swing_mode):
        """Set new target swing."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate swing choice: %s", swing_mode.upper())
        if swing_mode.upper() == 'ON':
            self._fujitsu_device.af_vertical_swing = 1
            self._fujitsu_device.af_horizontal_swing = 1
            _LOGGER.debug(self._name)
            _LOGGER.debug("FujitsuClimate swing choice valide: ON")
        if swing_mode.upper() == 'OFF':
            self._fujitsu_device.af_vertical_swing = 0
            self._fujitsu_device.af_horizontal_swing = 0
            _LOGGER.debug(self._name)
            _LOGGER.debug("FujitsuClimate swing choice valide: OFF")
        if swing_mode.upper() == 'VERTICAL':
            self._fujitsu_device.af_vertical_swing = 1
            self._fujitsu_device.af_horizontal_swing = 0
            _LOGGER.debug(self._name)
            _LOGGER.debug("FujitsuClimate swing choice valide: VERTICAL")
        if swing_mode.upper() == 'HORIZONTAL':
            self._fujitsu_device.af_vertical_swing = 0
            self._fujitsu_device.af_horizontal_swing = 1
            _LOGGER.debug(self._name)
            _LOGGER.debug("FujitsuClimate swing choice valide: HORIZONTAL")
       
        #if swing_mode.upper() == 'BOTH':
        #    self._fujitsu_device.af_vertical_swing = 1
        #    self._fujitsu_device.af_horizontal_swing = 1
        #    _LOGGER.debug("FujitsuClimate swing choice valide: BOTH")

    @property
    def preset_mode(self):
        """Return the preset setting."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate preset eco setting: %s", self._fujitsu_device.economy_mode['value'])
        _LOGGER.debug("FujitsuClimate preset boost setting: %s", self._fujitsu_device.powerful_mode['value'])
        if self._fujitsu_device.economy_mode['value'] == 1:
            return PRESET_ECO
        if self._fujitsu_device.powerful_mode['value'] == 1:
            return PRESET_BOOST
        return PRESET_NONE

    @property
    def preset_modes(self):
        """List of available preset modes."""
        return self._preset_modes

    def set_preset_mode(self, preset_mode):
        """Set preset mode."""
        _LOGGER.debug(self._name)
        _LOGGER.debug("FujitsuClimate preset choice: %s", preset_mode.upper())
        if preset_mode == PRESET_NONE:
            self._fujitsu_device.economy_mode = 0
            self._fujitsu_device.powerful_mode = 0
        elif preset_mode == PRESET_ECO:
            self._fujitsu_device.economy_mode = 1
        elif preset_mode == PRESET_BOOST:
            self._fujitsu_device.powerful_mode = 1
    
    ############old stufffff

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this thermostat."""
        return '_'.join([self._name, 'climate'])

    @property
    def should_poll(self):
        """Polling is required."""
        return True

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS
