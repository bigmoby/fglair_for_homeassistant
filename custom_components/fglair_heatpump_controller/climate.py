"""Support for the Fujitsu General Split A/C Wifi platform AKA FGLair ."""

import asyncio
from contextlib import suppress
from datetime import datetime
import logging
from typing import Any

from homeassistant.components.climate import (
    PLATFORM_SCHEMA,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
)
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_DIFFUSE,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_NONE,
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
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import Throttle
from homeassistant.util.dt import utcnow
from pyfujitsugeneral.client import FGLairApiClient
from pyfujitsugeneral.exceptions import FGLairGeneralException
from pyfujitsugeneral.splitAC import SplitAC, get_prop_from_json
import voluptuous as vol

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


async def _async_retry_api_call(
    api_call, max_retries: int = 3, delay: float = 1.0
) -> Any:
    """Retry API calls with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await api_call()
        except FGLairGeneralException as ex:
            if attempt == max_retries - 1:
                _LOGGER.error("API call failed after %d attempts: %s", max_retries, ex)
                raise HomeAssistantError(f"Device communication failed: {ex}") from ex
            _LOGGER.warning(
                "API call failed (attempt %d/%d): %s. Retrying in %.1fs...",
                attempt + 1,
                max_retries,
                ex,
                delay,
            )
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff
        except Exception as ex:
            _LOGGER.error("Unexpected error during API call: %s", ex)
            raise HomeAssistantError(f"Unexpected device error: {ex}") from ex


SUPPORT_FLAGS: ClimateEntityFeature = (
    ClimateEntityFeature.FAN_MODE
    | ClimateEntityFeature.SWING_MODE
    | ClimateEntityFeature.TARGET_TEMPERATURE
    | ClimateEntityFeature.PRESET_MODE
    | ClimateEntityFeature.TURN_ON
    | ClimateEntityFeature.TURN_OFF
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_REGION): cv.string,
        vol.Optional("tokenpath", default=DEFAULT_TOKEN_PATH): cv.string,
        vol.Optional("temperature_offset", default=DEFAULT_TEMPERATURE_OFFSET): vol.All(
            vol.Coerce(float), vol.Range(min=-5, max=5)
        ),
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

FUJITSU_TO_ACTION_LOOKUP = {
    "Normal": HVACAction.HEATING,
    # Heat pump cannot heat in this mode, but will be ready soon
    "Defrost": HVACAction.PREHEATING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setups the FujitsuClimate Platform based on a config entry."""
    _LOGGER.debug("FujitsuClimate async_setup_entry called")

    coordinator: FglairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

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


class FujitsuClimate(CoordinatorEntity[FglairDataUpdateCoordinator], ClimateEntity):
    # pylint: disable=R0902,R0904,R0913
    """Representation of a Fujitsu HVAC device."""

    _enable_turn_on_off_backwards_compatibility = False

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

        self._attr_supported_features = SUPPORT_FLAGS

        self._properties = None
        self._name = ""
        self._unique_id: str = ""
        self._aux_heat: bool = False
        self._current_temperature: float | None = None
        self._target_temperature: float | None = None
        self._fan_mode = None
        self._hvac_mode = None
        self._swing_modes: list[str] | None = None
        self._swing_mode: str | None = None
        self._swing_horizontal_modes: list[str] | None = None
        self._swing_horizontal_mode: str | None = None
        self._fan_modes: list[Any] = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
            FAN_DIFFUSE,
        ]
        self._hvac_modes: list[HVACMode] = SUPPORTED_MODES

    def get_supported_presets(self) -> list[str]:
        """Return list of supported preset modes based on device properties."""
        supported = [PRESET_NONE]  # Always include 'none'

        props: dict[str, Any] = self._properties or {}

        if get_prop_from_json("economy_mode", props):
            supported.append(PRESET_ECO)
        if get_prop_from_json("powerful_mode", props):
            supported.append(PRESET_BOOST)
        if get_prop_from_json("min_heat", props):
            supported.append(PRESET_AWAY)

        return supported

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

        return bool(self._fujitsu_device.get_powerful_mode()["value"])

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature in degrees Celsius."""
        return self._current_temperature

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (target_temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            rounded_temperature = self.round_off_temperature(target_temperature)
            _LOGGER.debug(
                "FujitsuClimate device [%s] set_temperature [%s] will be"
                " rounded with [%s]",
                self._name,
                target_temperature,
                rounded_temperature,
            )
            await _async_retry_api_call(
                lambda: self._fujitsu_device.async_change_temperature(
                    rounded_temperature
                )
            )
        else:
            _LOGGER.error(
                "FujitsuClimate device [%s] A target temperature must be provided",
                self._name,
            )

    def round_off_temperature(self, temperature: float) -> float:
        """Round temperature to the closest half."""
        return round(temperature * 2) / 2

    async def async_target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        try:
            data = await _async_retry_api_call(
                self._fujitsu_device.async_get_adjust_temperature_degree
            )
        except HomeAssistantError:
            # Return None if API fails - retry logic already logged the error
            return None
        else:
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
        return self._fujitsu_device.get_operation_mode()["value"] != 0

    @property
    def hvac_mode(self) -> Any:
        """Return current operation ie. heat, cool, idle."""
        operation_mode_desc = self._fujitsu_device.get_operation_mode_desc()
        label_state = FUJITSU_TO_HA_STATE.get(operation_mode_desc)

        operation_mode_value = self._fujitsu_device.get_operation_mode().get(
            "value", "Unknown"
        )

        _LOGGER.debug(
            "FujitsuClimate device [%s] return current operation_mode [%s] ;"
            " operation_mode_desc [%s] ; translated into [%s]",
            self._name,
            operation_mode_value,
            operation_mode_desc,
            label_state,
        )
        return label_state

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
            raise ServiceValidationError(f"Unsupported HVAC mode: {hvac_mode}")

        if hvac_mode == HVACMode.OFF:
            await _async_retry_api_call(self._fujitsu_device.async_turnOff)
        else:
            await _async_retry_api_call(
                lambda: self._fujitsu_device.async_change_operation_mode(
                    HA_STATE_TO_FUJITSU.get(hvac_mode)
                )
            )

        _LOGGER.debug(
            "FujitsuClimate device [%s] set_hvac_mode called. Current mode"
            " [%s] new will be [%s]",
            self._name,
            self._hvac_mode,
            hvac_mode,
        )

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation."""
        # HVACAction.IDLE is not (yet) managed by underlying pyfujitsugeneral library
        if not self.is_on:
            return HVACAction.OFF

        op_status_desc = self._fujitsu_device.get_op_status_desc()

        _LOGGER.debug(
            "Getting hvac_action on FujitsuClimate device [%s]: [%s]",
            self._name,
            op_status_desc,
        )

        if op_status_desc == "Normal":
            operation_mode = self._fujitsu_device.get_operation_mode_desc()
            label_state = FUJITSU_TO_HA_STATE.get(operation_mode)

            return {
                HVACMode.HEAT: HVACAction.HEATING,
                HVACMode.COOL: HVACAction.COOLING,
                HVACMode.DRY: HVACAction.DRYING,
                HVACMode.FAN_ONLY: HVACAction.FAN,
            }.get(label_state)

        if op_status_desc == "Defrost":
            return HVACAction.PREHEATING

        return None

    async def async_turn_on(self) -> None:
        """Set the HVAC State to on."""
        _LOGGER.debug("Turning on FujitsuClimate device [%s]", self._name)
        await _async_retry_api_call(self._fujitsu_device.async_turnOn)

    async def async_turn_off(self) -> None:
        """Set the HVAC State to off."""
        _LOGGER.debug("Turning off FujitsuClimate device [%s]", self._name)
        await _async_retry_api_call(self._fujitsu_device.async_turnOff)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Retrieve latest state."""
        _LOGGER.debug("Update FujitsuClimate device by async_update")

        try:
            self._properties = await _async_retry_api_call(
                self._fujitsu_device.async_update_properties
            )
        except HomeAssistantError:
            # Skip update if API fails - retry logic already logged the error
            return

        self._name = self.name  # ensure name is current

        _LOGGER.debug(
            "FujitsuClimate device [%s] detected supported presets: %s",
            self._name,
            self.get_supported_presets(),
        )

        self._name = self.name
        self._unique_id = self.unique_id
        self._aux_heat = self.is_aux_heat_on

        with suppress(HomeAssistantError):
            self._current_temperature = await _async_retry_api_call(
                self._fujitsu_device.async_get_display_temperature_degree
            )

        try:
            await self._async_refresh_display_temperature_request(
                self._fujitsu_device.get_refresh()["data_updated_at"]
            )
        except (HomeAssistantError, KeyError) as ex:
            _LOGGER.warning(
                "Failed to refresh display temperature for device %s: %s",
                self._name,
                ex,
            )

        self._target_temperature = await self.async_target_temperature()
        self._fan_mode = self.fan_mode
        self._hvac_mode = self.hvac_mode
        self._swing_modes = self.swing_modes
        self._swing_mode = self.swing_mode
        self._swing_horizontal_modes = self.swing_horizontal_modes
        self._swing_horizontal_mode = self.swing_horizontal_mode
        self._fan_modes = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
            FAN_DIFFUSE,
        ]
        self._hvac_modes = SUPPORTED_MODES
        self._preset_modes = [PRESET_NONE, PRESET_ECO, PRESET_BOOST, PRESET_AWAY]
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
        _LOGGER.debug("Last refreshed update date [%s]", refreshed_data_updated_at)
        must_be_refreshed = utcnow() > (
            refreshed_data_updated_at + REFRESH_MINUTES_INTERVAL
        )

        if must_be_refreshed:
            _LOGGER.debug("display_temperature will be refreshed in async mode")
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
        await _async_retry_api_call(
            lambda: self._fujitsu_device.async_changeFanSpeed(new_fan_speed)
        )

    @property
    def swing_mode(self) -> str | None:
        """Return the swing setting."""
        try:
            # Returns vertical settings, horizontal setting except for swing ignored
            vane_vertical_value = self._fujitsu_device.vane_vertical()

            # Use helper methods for safer access to swing values
            swing_vertical = self._fujitsu_device.get_swing_vertical_value()
            swing_horizontal = self._fujitsu_device.get_swing_horizontal_value()

            _LOGGER.debug(
                "FujitsuClimate device [%s] vertical swing value: %s, horizontal swing"
                " value: %s",
                self._name,
                swing_vertical,
                swing_horizontal,
            )

            if swing_vertical and swing_horizontal:
                mode = SWING_BOTH
            elif swing_vertical:
                mode = SWING_VERTICAL
            else:
                mode = VERTICAL + str(vane_vertical_value)

            self._swing_mode = mode

        except Exception as e:
            _LOGGER.error(
                "Error occurred while getting swing mode for device [%s]: %s",
                self._name,
                str(e),
            )
            return None
        else:
            _LOGGER.debug(
                "FujitsuClimate device [%s] mode value: %s",
                self._name,
                self._swing_mode,
            )
            return self._swing_mode

    @property
    def swing_modes(self) -> list[str] | None:
        """List of available swing modes."""

        vert_pos_list = self._fujitsu_device.vane_vertical_positions()
        hori_pos_list = self._fujitsu_device.vane_horizontal_positions()

        pos_list: list[str] = []

        # Add swing modes to the list if supported
        modes_list = self._fujitsu_device.get_swing_modes_supported()

        if modes_list == "Both":
            pos_list.append(SWING_VERTICAL)
            pos_list.append(SWING_HORIZONTAL)
            pos_list.append(SWING_BOTH)
            if vert_pos_list:
                pos_list += [VERTICAL + str(itm) for itm in vert_pos_list]
            if hori_pos_list:
                pos_list += [HORIZONTAL + str(itm) for itm in hori_pos_list]
        elif modes_list == "Vertical":
            pos_list.append(SWING_VERTICAL)
            if vert_pos_list:
                pos_list += [VERTICAL + str(itm) for itm in vert_pos_list]
        elif modes_list == "Horizontal":
            pos_list.append(SWING_HORIZONTAL)
            if hori_pos_list:
                pos_list += [HORIZONTAL + str(itm) for itm in hori_pos_list]

        # If pos_list is empty, return None instead of an empty list
        if not pos_list:
            _LOGGER.debug(
                "FujitsuClimate device [%s] returning swing modes: None", self._name
            )
            return None

        self._swing_modes = pos_list

        _LOGGER.debug(
            "FujitsuClimate device [%s] returning swing modes [%s]",
            self._name,
            self._swing_modes,
        )

        return self._swing_modes

    @property
    def swing_horizontal_mode(self) -> str | None:
        """Return the horizontal swing setting."""
        try:
            # First check if the device supports horizontal swing at all
            modes_list = self._fujitsu_device.get_swing_modes_supported()
            # Handle both string and list return types
            if isinstance(modes_list, list):
                modes_str = " ".join(modes_list).lower()
            else:
                modes_str = str(modes_list).lower() if modes_list else ""

            # If device doesn't support horizontal swing, return None
            if not modes_list or "horizontal" not in modes_str:
                _LOGGER.debug(
                    "FujitsuClimate device [%s] does not support horizontal swing",
                    self._name,
                )
                return None

            swing_horizontal = self._fujitsu_device.get_swing_horizontal_value()
            _LOGGER.debug(
                "FujitsuClimate device [%s] horizontal swing value: %s",
                self._name,
                swing_horizontal,
            )
            if swing_horizontal:
                mode = SWING_HORIZONTAL
            else:
                # When horizontal swing is off, try to get the current horizontal
                # position. This is consistent with how swing_mode handles vertical
                # positions
                try:
                    # Try to get current horizontal position if available
                    # Note: This assumes there's a method to get current horizontal
                    # position. If not available, we'll fall back to None
                    if hasattr(self._fujitsu_device, "vane_horizontal"):
                        vane_horizontal_value = self._fujitsu_device.vane_horizontal()
                        mode = HORIZONTAL + str(vane_horizontal_value)
                    else:
                        # Fallback: return None if no method to get current position
                        mode = None
                except Exception:
                    # If we can't get the current position, return None
                    mode = None
            self._swing_horizontal_mode = mode
            _LOGGER.debug(
                "FujitsuClimate device [%s] horizontal swing mode: %s",
                self._name,
                self._swing_horizontal_mode,
            )
        except Exception as ex:
            _LOGGER.error(
                "Error getting horizontal swing mode for device [%s]: %s",
                self._name,
                ex,
            )
            return None
        else:
            return self._swing_horizontal_mode

    @property
    def swing_horizontal_modes(self) -> list[str] | None:
        """List of available horizontal swing modes."""
        try:
            pos_list: list[str] = []
            modes_list = self._fujitsu_device.get_swing_modes_supported()
            # Handle both string and list return types
            if isinstance(modes_list, list):
                modes_str = " ".join(modes_list).lower()
            else:
                modes_str = str(modes_list).lower() if modes_list else ""

            if modes_list and "horizontal" in modes_str:
                pos_list.append(SWING_HORIZONTAL)
                try:
                    horizontal_positions = (
                        self._fujitsu_device.get_horizontal_positions()
                    )
                    if horizontal_positions:
                        # PERF401: usare una list comprehension
                        pos_list.extend(
                            [f"{HORIZONTAL}{pos}" for pos in horizontal_positions]
                        )
                except Exception:
                    pass
            if not pos_list:
                _LOGGER.debug(
                    "Device [%s] does not support horizontal swing modes",
                    self._name,
                )
                return None
            self._swing_horizontal_modes = pos_list
            _LOGGER.debug(
                "FujitsuClimate device [%s] returning horizontal swing modes [%s]",
                self._name,
                self._swing_horizontal_modes,
            )
        except Exception as ex:
            _LOGGER.error(
                "Error getting horizontal swing modes for device [%s]: %s",
                self._name,
                ex,
            )
            return None
        else:
            return self._swing_horizontal_modes

    async def async_set_swing_horizontal_mode(self, swing_horizontal_mode: Any) -> None:
        """Set new target horizontal swing."""
        try:
            modes_list = self._fujitsu_device.get_swing_modes_supported()
            # Handle both string and list return types
            if isinstance(modes_list, list):
                modes_str = " ".join(modes_list).lower()
            else:
                modes_str = str(modes_list).lower() if modes_list else ""

            if not modes_list or "horizontal" not in modes_str:
                _LOGGER.warning(
                    "FujitsuClimate device [%s] does not support horizontal swing mode",
                    self._name,
                )
                return
            if swing_horizontal_mode == SWING_HORIZONTAL:
                await _async_retry_api_call(
                    lambda: self._fujitsu_device.async_set_af_horizontal_swing(1)
                )
            elif isinstance(
                swing_horizontal_mode, str
            ) and swing_horizontal_mode.startswith(HORIZONTAL):
                # Extract the position number after "Horizontal"
                position_str = swing_horizontal_mode[len(HORIZONTAL) :]
                try:
                    position = int(position_str)
                    await _async_retry_api_call(
                        lambda: self._fujitsu_device.async_set_vane_horizontal_position(
                            position
                        )
                    )
                except ValueError as ex:
                    _LOGGER.error(
                        "Invalid horizontal position '%s' for device [%s]: %s",
                        position_str,
                        self._name,
                        ex,
                    )
                    raise HomeAssistantError(
                        f"Invalid horizontal position: {position_str}"
                    ) from ex
            else:
                _LOGGER.error(
                    "Invalid horizontal swing mode '%s' for device [%s]",
                    swing_horizontal_mode,
                    self._name,
                )
                raise HomeAssistantError(
                    f"Invalid horizontal swing mode: {swing_horizontal_mode}"
                )
            _LOGGER.debug(
                "FujitsuClimate device [%s] horizontal swing choice [%s]",
                self._name,
                swing_horizontal_mode,
            )
        except Exception as ex:
            _LOGGER.error(
                "Error setting horizontal swing mode for device [%s]: %s",
                self._name,
                ex,
            )
            raise HomeAssistantError(
                f"Failed to set horizontal swing mode: {ex}"
            ) from ex

    async def async_set_swing_mode(self, swing_mode: Any) -> None:
        """Set new target swing."""
        # Note setting one direction will not affect other, except swing both
        if swing_mode == SWING_VERTICAL:
            await _async_retry_api_call(
                lambda: self._fujitsu_device.async_set_af_vertical_swing(1)
            )
        elif swing_mode == SWING_HORIZONTAL:
            await _async_retry_api_call(
                lambda: self._fujitsu_device.async_set_af_horizontal_swing(1)
            )
        elif swing_mode == SWING_BOTH:
            await _async_retry_api_call(
                lambda: self._fujitsu_device.async_set_af_vertical_swing(1)
            )
            await _async_retry_api_call(
                lambda: self._fujitsu_device.async_set_af_horizontal_swing(1)
            )
        elif isinstance(swing_mode, str) and swing_mode.startswith(VERTICAL):
            # Extract the position number after "Vertical"
            position_str = swing_mode[len(VERTICAL) :]
            if not position_str:
                raise HomeAssistantError("Empty vertical position")
            try:
                position = int(position_str)
                await _async_retry_api_call(
                    lambda: self._fujitsu_device.async_set_vane_vertical_position(
                        position
                    )
                )
            except ValueError as ex:
                _LOGGER.error(
                    "Invalid vertical position '%s' for device [%s]: %s",
                    position_str,
                    self._name,
                    ex,
                )
                raise HomeAssistantError(
                    f"Invalid vertical position: {position_str}"
                ) from ex
        elif isinstance(swing_mode, str) and swing_mode.startswith(HORIZONTAL):
            # Extract the position number after "Horizontal"
            position_str = swing_mode[len(HORIZONTAL) :]
            if not position_str:
                raise HomeAssistantError("Empty horizontal position")
            try:
                position = int(position_str)
                await _async_retry_api_call(
                    lambda: self._fujitsu_device.async_set_vane_horizontal_position(
                        position
                    )
                )
            except ValueError as ex:
                _LOGGER.error(
                    "Invalid horizontal position '%s' for device [%s]: %s",
                    position_str,
                    self._name,
                    ex,
                )
                raise HomeAssistantError(
                    f"Invalid horizontal position: {position_str}"
                ) from ex
        _LOGGER.debug(
            "FujitsuClimate device [%s] swing choice [%s]",
            self._name,
            swing_mode,
        )

    @property
    def preset_mode(self) -> Any:
        """Return the preset setting."""
        properties = self._fujitsu_device.get_properties()

        # Check if all preset props are missing
        if (
            not get_prop_from_json("economy_mode", properties)
            and not get_prop_from_json("powerful_mode", properties)
            and not get_prop_from_json("min_heat", properties)
        ):
            _LOGGER.debug(
                "FujitsuClimate device [%s] has no preset props",
                self._name,
            )
            return PRESET_NONE

        # Use helper methods for safer access to preset values
        eco_value = self._fujitsu_device.get_economy_mode_value()
        boost_value = self._fujitsu_device.get_powerful_mode_value()
        min_heat_value = self._fujitsu_device.get_min_heat_value()

        if eco_value:
            _LOGGER.debug(
                "FujitsuClimate device [%s] preset eco setting: %s",
                self._name,
                eco_value,
            )
            return PRESET_ECO

        if boost_value:
            _LOGGER.debug(
                "FujitsuClimate device [%s] preset boost setting: %s",
                self._name,
                boost_value,
            )
            return PRESET_BOOST

        if min_heat_value:
            _LOGGER.debug(
                "FujitsuClimate device [%s] preset min_heat (or away) setting: %s",
                self._name,
                min_heat_value,
            )
            return PRESET_AWAY

        return PRESET_NONE

    @property
    def preset_modes(self) -> list[str]:
        """Return the supported preset modes for this device."""
        return self.get_supported_presets()

    async def async_set_preset_mode(self, preset_mode: Any) -> None:
        """Set preset mode."""
        _LOGGER.debug(
            "FujitsuClimate device [%s] preset choice: %s",
            self._name,
            str(preset_mode).upper(),
        )

        def has_valid_key(prop):
            return isinstance(prop, dict) and "key" in prop and prop["key"] is not None

        if preset_mode == PRESET_NONE:
            if has_valid_key(self._fujitsu_device.get_economy_mode()):
                await self._fujitsu_device.async_economy_mode_off()
            if has_valid_key(self._fujitsu_device.get_powerful_mode()):
                await self._fujitsu_device.async_powerful_mode_off()
            if has_valid_key(self._fujitsu_device.get_min_heat()):
                await self._fujitsu_device.async_min_heat_mode_off()

        elif preset_mode == PRESET_ECO:
            if has_valid_key(self._fujitsu_device.get_powerful_mode()):
                await self._fujitsu_device.async_powerful_mode_off()
            if has_valid_key(self._fujitsu_device.get_min_heat()):
                await self._fujitsu_device.async_min_heat_mode_off()
            if has_valid_key(self._fujitsu_device.get_economy_mode()):
                await self._fujitsu_device.async_economy_mode_on()

        elif preset_mode == PRESET_BOOST:
            if has_valid_key(self._fujitsu_device.get_economy_mode()):
                await self._fujitsu_device.async_economy_mode_off()
            if has_valid_key(self._fujitsu_device.get_min_heat()):
                await self._fujitsu_device.async_min_heat_mode_off()
            if has_valid_key(self._fujitsu_device.get_powerful_mode()):
                await self._fujitsu_device.async_powerful_mode_on()

        elif preset_mode == PRESET_AWAY:
            if has_valid_key(self._fujitsu_device.get_economy_mode()):
                await self._fujitsu_device.async_economy_mode_off()
            if has_valid_key(self._fujitsu_device.get_powerful_mode()):
                await self._fujitsu_device.async_powerful_mode_off()
            if has_valid_key(self._fujitsu_device.get_min_heat()):
                await self._fujitsu_device.async_min_heat_mode_on()

        # Refresh device properties (to reflect latest mode)
        await self._fujitsu_device.async_update_properties()
        self._properties = self._fujitsu_device.get_properties()

        # Also update entity internal state cache and Home Assistant UI
        await self.async_update()

        _LOGGER.debug(
            "FujitsuClimate device [%s] preset mode set and updated",
            self._name,
        )

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
        features = SUPPORT_FLAGS
        try:
            modes_list = self._fujitsu_device.get_swing_modes_supported()
            # Handle both string and list return types
            if isinstance(modes_list, list):
                modes_str = " ".join(modes_list).lower()
            else:
                modes_str = str(modes_list).lower() if modes_list else ""

            if modes_list and "horizontal" in modes_str:
                features |= ClimateEntityFeature.SWING_HORIZONTAL_MODE
                _LOGGER.debug(
                    "FujitsuClimate device [%s] supports horizontal swing mode",
                    self._name,
                )
            else:
                _LOGGER.debug(
                    "FujitsuClimate device [%s] does not support horizontal swing mode",
                    self._name,
                )
        except Exception as ex:
            _LOGGER.debug(
                "Device [%s] error checking horizontal swing support: %s",
                self._name,
                ex,
            )
        return features
