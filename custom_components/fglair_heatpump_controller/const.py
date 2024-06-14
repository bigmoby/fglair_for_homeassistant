"""Constants for FGLair Home Assistant Integration."""

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform

# Base component constants
NAME = "FGLair Home Assistant Integration"
DOMAIN = "fglair_heatpump_controller"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.3.13"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/bigmoby/fglair_for_homeassistant/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
PLATFORMS = [Platform.CLIMATE]

# Configuration and options
CONF_TOKENPATH = "tokenpath"
CONF_TEMPERATURE_OFFSET = "temperature_offset"

DEFAULT_TEMPERATURE_OFFSET: float = 2.0
DEFAULT_TOKEN_PATH = "token.txt"

MIN_TEMP = 16
MAX_TEMP = 30

DEFAULT_MIN_STEP: Final = 0.5

VERTICAL = "Vertical_"
HORIZONTAL = "Horizontal_"

SCAN_INTERVAL = timedelta(seconds=60)
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)
REFRESH_MINUTES_INTERVAL = timedelta(minutes=3)

DEFAULT_TIMEOUT = 60

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
