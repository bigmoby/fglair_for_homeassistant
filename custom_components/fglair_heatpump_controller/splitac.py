from typing import Any

import logging
import numpy as np

from .client import FGLairApiClient
from .exceptions import FGLairMethodException, FGLairGeneralException


_LOGGER = logging.getLogger(__name__)


def get_prop_from_json(property_name: str, properties: Any) -> dict[str, Any]:
    data = {}
    for property_item in properties:
        if property_item["property"]["name"] == property_name:
            data = {
                "value": property_item["property"]["value"],
                "key": property_item["property"]["key"],
            }
    return data


class SplitAC:
    def __init__(
        self,
        dsn: str,
        client: FGLairApiClient,
        tokenpath: str,
        temperature_offset: float,
    ) -> None:
        self._dsn = dsn
        self._client = client  # Setting the API object
        self._tokenpath = tokenpath
        self._temperature_offset = temperature_offset
        self.set_properties(None)
        self._device_name: dict[str, str] = {}
        self._af_vertical_swing: dict[str, bool] = {}
        self._af_vertical_direction: dict[str, int] = {}
        self._af_vertical_num_dir: dict[str, int] = {}
        self._af_horizontal_swing: dict[str, bool] = {}
        self._af_horizontal_direction: dict[str, int] = {}
        self._af_horizontal_num_dir: dict[str, int] = {}
        self._economy_mode: dict[str, bool] = {}
        self._fan_speed: dict[str, int] = {}
        self._powerful_mode: dict[str, bool] = {}
        self._min_heat: dict[str, bool] = {}
        self._outdoor_low_noise: dict[str, bool] = {}
        self._operation_mode: dict[str, int] = {}
        self._adjust_temperature: dict[str, int] = {}
        self._display_temperature: dict[str, int] = {}
        self._outdoor_temperature: dict[str, int] = {}

        # self.properties: For now this variable is not used but lots of device properties which are not implemented
        # this variable can be used to expose those properties and implement them.
        # self.async_update_properties()

    # Method for getting new (refreshing) properties values
    async def async_update_properties(self) -> Any:
        self.set_properties(await self._client.async_get_device_properties(self._dsn))
        self.set_device_name(self.get_properties())
        await self.async_set_af_vertical_swing(self.get_properties())
        await self.async_set_af_vertical_direction(self.get_properties())
        self.set_af_vertical_num_dir(self.get_properties())
        await self.async_set_af_horizontal_swing(self.get_properties())
        await self.async_set_af_horizontal_direction(self.get_properties())
        self.set_af_horizontal_num_dir(self.get_properties())
        await self.async_set_economy_mode(self.get_properties())
        await self.async_set_fan_speed(self.get_properties())
        await self.async_set_powerful_mode(self.get_properties())
        await self.async_set_min_heat(self.get_properties())
        await self.async_set_outdoor_low_noise(self.get_properties())
        await self.async_set_operation_mode(self.get_properties())
        await self.async_set_adjust_temperature(self.get_properties())
        await self.async_set_display_temperature(self.get_properties())
        await self.async_set_outdoor_temperature(self.get_properties())
        return self.get_properties()

    # To Turn on the device get the last operation mode using property history method
    # Find the last not 'OFF'/'0' O.M.
    # Turn on by setting O.M. to the last O.M
    async def async_turnOn(self) -> None:
        datapoints = await self._async_get_device_property_history(
            self.get_operation_mode()["key"]
        )
        # Get the latest setting before turn off
        for datapoint in reversed(datapoints):
            if datapoint["datapoint"]["value"] != 0:
                last_operation_mode = int(datapoint["datapoint"]["value"])
                break

        await self.async_set_operation_mode(last_operation_mode)
        await self.async_update_properties()

    async def async_turnOff(self) -> None:
        await self.async_set_operation_mode(0)
        await self.async_update_properties()

    # Economy mode setting
    async def async_economy_mode_on(self) -> None:
        await self.async_set_economy_mode(1)

    async def async_economy_mode_off(self) -> None:
        await self.async_set_economy_mode(0)

    # Powerfull mode setting
    async def async_powerfull_mode_on(self) -> None:
        await self.async_set_powerful_mode(1)

    async def async_powerfull_mode_off(self) -> None:
        await self.async_set_powerful_mode(0)

    # Fan speed setting
    # Quiet Low Medium High Auto
    async def async_changeFanSpeed(self, speed: str) -> None:
        if speed.upper() == "QUIET":
            await self.async_fan_speed_quiet()
            return None
        if speed.upper() == "LOW":
            await self.async_fan_speed_low()
            return None
        if speed.upper() == "MEDIUM":
            await self.async_fan_speed_medium()
            return None
        if speed.upper() == "HIGH":
            await self.async_fan_speed_high()
            return None
        if speed.upper() == "AUTO":
            await self.async_fan_speed_auto()
            return None

    async def async_fan_speed_quiet(self) -> None:
        await self.async_set_fan_speed(0)

    async def async_fan_speed_low(self) -> None:
        await self.async_set_fan_speed(1)

    async def async_fan_speed_medium(self) -> None:
        await self.async_set_fan_speed(2)

    async def async_fan_speed_high(self) -> None:
        await self.async_set_fan_speed(3)

    async def async_fan_speed_auto(self) -> None:
        await self.async_set_fan_speed(4)

    def get_fan_speed_desc(self) -> str:
        FAN_SPEED_DICT = {0: "Quiet", 1: "Low", 2: "Medium", 3: "High", 4: "Auto"}
        return FAN_SPEED_DICT[self.get_fan_speed()["value"]]

    def get_swing_modes_supported(self) -> str:
        SWING_DICT = {0: "None", 1: "Vertical", 2: "Horizontal", 3: "Both"}
        key = 0
        if self.get_af_vertical_direction()["value"] is not None:
            key = key | 1
        if self.get_af_horizontal_direction()["value"] is not None:
            key = key | 2
        return SWING_DICT[key]

    # Vertical
    async def async_vertical_swing_on(self) -> None:
        await self.async_set_af_vertical_swing(1)

    async def async_vertical_swing_off(self) -> None:
        await self.async_set_af_vertical_swing(0)

    def vane_vertical_positions(self) -> list[str]:
        """Return available vertical vane positions."""
        array = np.arange(1, self.get_af_vertical_num_dir()["value"] + 1)
        return list(array)

    def vane_vertical(self) -> int:
        """Return vertical vane position."""
        return self.get_af_vertical_direction()["value"]

    async def async_set_vane_vertical_position(self, pos: int) -> None:
        """Set vertical vane position."""
        if pos >= 1 and pos <= self.get_af_vertical_num_dir()["value"]:
            await self.async_set_af_vertical_swing(0)
            await self.async_set_af_vertical_direction(pos)
        else:
            raise FGLairGeneralException("Vane position not supported")

    # Horizontal
    async def async_horizontal_swing_on(self) -> None:
        await self.async_set_af_horizontal_swing(1)

    async def async_horizontal_swing_off(self) -> None:
        await self.async_set_af_horizontal_swing(0)

    def vane_horizontal_positions(self) -> list[str]:
        """Return available horizontal vane positions."""
        array = np.arange(1, self.get_af_horizontal_num_dir()["value"] + 1)
        return list(array)

    def vane_horizontal(self) -> int:
        """Return horizontal vane position."""
        return self.get_af_horizontal_direction()["value"]

    async def async_set_vane_horizontal_position(self, pos: int) -> None:
        """Set horizontal vane position."""
        if pos >= 1 and pos <= self.get_af_horizontal_num_dir()["value"]:
            await self.async_set_af_horizontal_swing(0)
            await self.async_set_af_horizontal_direction(pos)
        else:
            raise FGLairGeneralException("Vane position not supported")

    # Temperature setting
    async def async_changeTemperature(self, newTemperature: int | float) -> None:
        # set temperature for degree C
        if not isinstance(newTemperature, int) and not isinstance(
            newTemperature, float
        ):
            raise FGLairMethodException("Wrong usage of method")
        # Fixing temps if not given as multiplies of 10 less than 160
        if newTemperature < 160:
            newTemperature = newTemperature * 10
        if newTemperature >= 160 and newTemperature <= 320:
            await self.async_set_adjust_temperature(newTemperature)
        else:
            raise FGLairGeneralException("temperature out of range!")

    # Operation Mode setting
    async def async_changeOperationMode(self, operation_mode: str | int | None) -> None:
        if operation_mode:
            if not isinstance(operation_mode, int):
                operation_mode = self._operation_mode_translate(operation_mode)
            await self.async_set_operation_mode(operation_mode)
        else:
            raise FGLairGeneralException("operation_mode cannot be None!")

    # Class properties:

    def get_dsn(self) -> str:
        return self._dsn

    def get_operation_mode(self) -> dict[str, int]:
        return self._operation_mode

    def get_operation_mode_desc(self) -> Any:
        return self._operation_mode_translate(self.get_operation_mode()["value"])

    async def async_set_operation_mode(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._operation_mode = get_prop_from_json("operation_mode", properties)
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_operation_mode()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    # property to get display temperature in degree Cs
    async def async_set_display_temperature_degree(self) -> float | None:
        data = None
        if self._adjust_temperature is not None:
            adjustTemperatureValue = self._adjust_temperature["value"]
            if adjustTemperatureValue == 65535:
                datapoints = await self._async_get_device_property_history(
                    self._adjust_temperature["key"]
                )
                # Get the latest setting other than invalid value
                for datapoint in reversed(datapoints):
                    if datapoint["datapoint"]["value"] != 65535:
                        adjustTemperatureValue = int(datapoint["datapoint"]["value"])
                        break
            data = round((adjustTemperatureValue / 10), 1)
        return data

    # property returns display temperature dict in 10 times of degree C
    def get_display_temperature(self) -> dict[str, int]:
        return self._display_temperature

    async def async_set_display_temperature(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._display_temperature = get_prop_from_json(
                "display_temperature", properties
            )
        elif isinstance(properties, int) or isinstance(properties, float):
            await self._client.async_set_device_property(
                self.get_display_temperature()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    # property to get outdoor temperature in degree C
    def get_outdoor_temperature_degree(self) -> float | None:
        data = None
        if self._outdoor_temperature is not None:
            data = round(((self._outdoor_temperature["value"] / 100 - 32) / 9 * 5), 1)
        return data

    # property returns outdoor temperature dict in 10 times of degree C
    def get_outdoor_temperature(self) -> dict[str, int]:
        return self._outdoor_temperature

    async def async_set_outdoor_temperature(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._outdoor_temperature = get_prop_from_json(
                "outdoor_temperature", properties
            )
        elif isinstance(properties, int) or isinstance(properties, float):
            await self._client.async_set_device_property(
                self.get_outdoor_temperature()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    # property to get temperature in degree C
    async def async_get_adjust_temperature_degree(self) -> float | None:
        data = None
        if self._adjust_temperature is not None:
            adjustTemperatureValue = self._adjust_temperature["value"]
            if adjustTemperatureValue == 65535:
                datapoints = await self._async_get_device_property_history(
                    self._adjust_temperature["key"]
                )
                # Get the latest setting other than invalid value
                for datapoint in reversed(datapoints):
                    if datapoint["datapoint"]["value"] != 65535:
                        adjustTemperatureValue = int(datapoint["datapoint"]["value"])
                        break
            data = round((adjustTemperatureValue / 10), 1)
        return data

    # property returns temperature dict in 10 times of degree C
    def get_adjust_temperature(self) -> dict[str, int]:
        return self._adjust_temperature

    async def async_set_adjust_temperature(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._adjust_temperature = get_prop_from_json(
                "adjust_temperature", properties
            )
        elif isinstance(properties, int) or isinstance(properties, float):
            await self._client.async_set_device_property(
                self.get_adjust_temperature()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_outdoor_low_noise(self) -> dict[str, bool]:
        return self._outdoor_low_noise

    async def async_set_outdoor_low_noise(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._outdoor_low_noise = get_prop_from_json(
                "outdoor_low_noise", properties
            )
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_outdoor_low_noise()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_powerful_mode(self) -> dict[str, bool]:
        return self._powerful_mode

    async def async_set_powerful_mode(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._powerful_mode = get_prop_from_json("powerful_mode", properties)
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_powerful_mode()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_properties(self) -> Any:
        return self._properties

    def set_properties(self, properties: Any) -> None:
        self._properties = properties

    def get_fan_speed(self) -> dict[str, int]:
        return self._fan_speed

    async def async_set_fan_speed(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._fan_speed = get_prop_from_json("fan_speed", properties)
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_fan_speed()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_min_heat(self) -> dict[str, bool]:
        return self._min_heat

    async def async_set_min_heat(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._min_heat = get_prop_from_json("min_heat", properties)
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_min_heat()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_economy_mode(self) -> dict[str, bool]:
        return self._economy_mode

    async def async_set_economy_mode(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._economy_mode = get_prop_from_json("economy_mode", properties)
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_economy_mode()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_af_horizontal_num_dir(self) -> dict[str, int]:
        return self._af_horizontal_num_dir

    def set_af_horizontal_num_dir(self, properties: Any) -> None:
        self._af_horizontal_num_dir = get_prop_from_json(
            "af_horizontal_num_dir", properties
        )

    def get_af_horizontal_direction(self) -> dict[str, int]:
        return self._af_horizontal_direction

    async def async_set_af_horizontal_direction(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._af_horizontal_direction = get_prop_from_json(
                "af_horizontal_direction", properties
            )
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_af_horizontal_direction()["key"], properties
            )
            await self.async_horizontal_swing_off()  # If direction set then swing will be turned OFF
            await self.async_update_properties()
        else:
            raise FGLairMethodException(
                "Wrong usage of the method or direction out of range!"
            )

    def get_af_horizontal_swing(self) -> dict[str, bool]:
        return self._af_horizontal_swing

    async def async_set_af_horizontal_swing(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._af_horizontal_swing = get_prop_from_json(
                "af_horizontal_swing", properties
            )
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_af_horizontal_swing()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_af_vertical_num_dir(self) -> dict[str, int]:
        return self._af_vertical_num_dir

    def set_af_vertical_num_dir(self, properties: Any) -> None:
        self._af_vertical_num_dir = get_prop_from_json(
            "af_vertical_num_dir", properties
        )

    def get_af_vertical_direction(self) -> dict[str, int]:
        return self._af_vertical_direction

    async def async_set_af_vertical_direction(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._af_vertical_direction = get_prop_from_json(
                "af_vertical_direction", properties
            )
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_af_vertical_direction()["key"], properties
            )
            await self.async_vertical_swing_off()  ##If direction set then swing will be turned OFF
            await self.async_update_properties()
        else:
            raise FGLairMethodException(
                "Wrong usage of the method or direction out of range!"
            )

    def get_af_vertical_swing(self) -> dict[str, bool]:
        return self._af_vertical_swing

    async def async_set_af_vertical_swing(self, properties: Any) -> None:
        if isinstance(properties, (list, tuple)):
            self._af_vertical_swing = get_prop_from_json(
                "af_vertical_swing", properties
            )
        elif isinstance(properties, int):
            await self._client.async_set_device_property(
                self.get_af_vertical_swing()["key"], properties
            )
            await self.async_update_properties()
        else:
            raise FGLairMethodException("Wrong usage of the method!")

    def get_device_name(self) -> dict[str, str]:
        return self._device_name

    def set_device_name(self, properties: Any) -> None:
        self._device_name = get_prop_from_json("device_name", properties)

    def get_op_status(self) -> dict[str, int]:
        return get_prop_from_json("op_status", self.get_properties())

    def get_op_status_desc(self) -> str | None:
        data = None
        if self.get_op_status() is not None:
            DICT_OP_MODE = {0: "Normal", 16777216: "Defrost"}
            status = self.get_op_status()["value"]
            data = (
                DICT_OP_MODE[status] if status in DICT_OP_MODE else f"Unknown {status}"
            )
            return data
        return data

    # Get a property history
    async def _async_get_device_property_history(self, property_code: int) -> Any:
        property_history = await self._client.async_get_device_property(property_code)
        return property_history

    # Translate the operation mode to descriptive values and reverse
    def _operation_mode_translate(self, operation_mode: str | int) -> Any:
        DICT_OPERATION_MODE = {
            "off": 0,
            "unknown": 1,
            "auto": 2,
            "cool": 3,
            "dry": 4,
            "fan_only": 5,
            "heat": 6,
            0: "off",
            1: "unknown",
            2: "auto",
            3: "cool",
            4: "dry",
            5: "fan_only",
            6: "heat",
        }
        return DICT_OPERATION_MODE[operation_mode]
