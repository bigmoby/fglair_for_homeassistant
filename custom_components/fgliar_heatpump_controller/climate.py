"""
Support for the Fujitsu General Split A/C Wifi platform AKA FGLair .
"""

import logging
import voluptuous as vol

from homeassistant.components.climate import ClimateEntity, PLATFORM_SCHEMA
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_AUTO,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_AUX_HEAT,
    FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_DIFFUSE,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE)
from homeassistant.const import (
    ATTR_TEMPERATURE, CONF_USERNAME, CONF_PASSWORD, TEMP_CELSIUS)
import homeassistant.helpers.config_validation as cv

__version__ = '0.9.20'

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['pyfujitsu==0.9.19']

# Values from web interface
MIN_TEMP = 17
MAX_TEMP = 24

SUPPORT_FLAGS = SUPPORT_FAN_MODE | SUPPORT_SWING_MODE | SUPPORT_TARGET_TEMPERATURE

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional('region'): cv.string,
    vol.Optional('tokenpath'): cv.string,

})

HA_FAN_TO_FUJITSU = {
    FAN_AUTO: "Auto",
    FAN_LOW: "Low",
    FAN_MEDIUM: "Medium",
    FAN_HIGH: "High",
    FAN_DIFFUSE: "Quiet"
}

FUJITSU_FAN_TO_HA = {
    "Auto": FAN_AUTO,
    "Low": FAN_LOW,
    "Medium": FAN_MEDIUM,
    "High": FAN_HIGH,
    "Quiet": FAN_DIFFUSE
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the E-Thermostaat Platform."""
    _LOGGER.debug("FujitsuClimate setup_platform called")
    import pyfujitsu.api as fgapi
    _LOGGER.debug("FujitsuClimate pyfujitsu.api import called")
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    region = config.get('region')
    tokenpath = config.get('tokenpath')
    _LOGGER.debug("FujitsuClimate config.get ")

    fglairapi = fgapi.Api(username, password, region, tokenpath)
    if not fglairapi._authenticate():
        _LOGGER.error("Unable to authenticate with Fujistsu General")
        return

    _LOGGER.debug("FujitsuClimate fglairapi._authenticate ")

    devices = fglairapi.get_devices_dsn()
    add_entities(FujitsuClimate(fglairapi, dsn) for dsn in devices)
    _LOGGER.debug("FujitsuClimate setup_platform fine")


class FujitsuClimate(ClimateEntity):
    """Representation of a E-Thermostaat device."""

    def __init__(self, api, dsn):
        """Initialize the thermostat."""
        _LOGGER.debug("FujitsuClimate init called for dsn: %s", dsn)
        import pyfujitsu.splitAC as splitAC
        _LOGGER.debug("FujitsuClimate pyfujitsu.splitAC called")
        self._api = api
        self._dsn = dsn
        self._fujitsu_device = splitAC.splitAC(self._dsn, self._api)
        _LOGGER.debug("FujitsuClimate _fujitsu_device setup.")
        self._name = self.name
        _LOGGER.debug("FujitsuClimate name set: %s", self._name)
        self._aux_heat = self.is_aux_heat_on
        self._target_temperature = self.target_temperature
        self._fan_mode = self.fan_mode
        self._hvac_mode = self.hvac_mode
        self._swing_mode = self.swing_mode

        self._fan_modes = [FUJITSU_FAN_TO_HA['Quiet'], FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_AUTO]
        self._hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY,
                            HVAC_MODE_OFF]
        self._swing_modes = ['Horizontal', 'Down', 'Unknown', 'Swing']
        self._on = self.is_on

        _LOGGER.debug("FujitsuClimate init fine.")

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._fujitsu_device.device_name['value']

    @property
    def is_aux_heat_on(self):
        """Reusing is for Powerfull mode."""
        if not hasattr(self._fujitsu_device.powerful_mode, 'value'):
            return False
        elif self._fujitsu_device.powerful_mode['value'] == 1:
            return True
        else:
            return False

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._fujitsu_device.adjust_temperature_degree

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def is_on(self):
        """Return true if on."""
        if self._fujitsu_device.operation_mode['value'] != 0:
            return True
        else:
            return False

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        return self._fujitsu_device.operation_mode_desc

    @property
    def hvac_modes(self):
        """HVAC modes."""
        return self._hvac_modes

    def set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""
        _LOGGER.debug("FujitsuClimate set_hvac_mode called. self._hvac_mode: %s ; hvac_mode: %s", self._hvac_mode,
                      hvac_mode)
        if (hvac_mode == HVAC_MODE_OFF):
            """Turn device off."""
            self._fujitsu_device.turnOff()
        elif (self._hvac_mode != hvac_mode):
            self._fujitsu_device.changeOperationMode(hvac_mode)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        _LOGGER.debug("FujitsuClimate set_temperature: %s ; 2: %s", kwargs.get(ATTR_TEMPERATURE),
                      kwargs.get(ATTR_TEMPERATURE))
        self._fujitsu_device.changeTemperature(kwargs.get(ATTR_TEMPERATURE))

    def update(self):
        """Retrieve latest state."""
        self._fujitsu_device.refresh_properties()

    @property
    def fan_mode(self):
        """Return the fan setting."""
        return FUJITSU_FAN_TO_HA[self._fujitsu_device.get_fan_speed_desc()]

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return self._fan_modes

    def set_fan_mode(self, fan_mode):
        """Set fan mode."""
        self._fujitsu_device.changeFanSpeed(HA_FAN_TO_FUJITSU[fan_mode])

    @property
    def swing_mode(self):
        """Return the fan setting."""
        return self._fujitsu_device.get_swing_mode_desc()

    @property
    def swing_modes(self):
        """List of available swing modes."""
        return self._swing_modes

    def set_swing_mode(self, swing_mode):
        """Set new target temperature."""
        self._fujitsu_device.changeSwingMode(swing_mode)

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
        return TEMP_CELSIUS

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS