"""Test constants."""

from datetime import timedelta

from custom_components.fglair_heatpump_controller.const import (
    ATTRIBUTION,
    BINARY_SENSOR_DEVICE_CLASS,
    DEFAULT_MIN_STEP,
    DEFAULT_NAME,
    DEFAULT_TEMPERATURE_OFFSET,
    DEFAULT_TIMEOUT,
    DEFAULT_TOKEN_PATH,
    DOMAIN,
    DOMAIN_DATA,
    HORIZONTAL,
    ICON,
    ISSUE_URL,
    MAX_TEMP,
    MIN_TEMP,
    MIN_TIME_BETWEEN_UPDATES,
    NAME,
    PLATFORMS,
    REFRESH_MINUTES_INTERVAL,
    SCAN_INTERVAL,
    STARTUP_MESSAGE,
    VERSION,
    VERTICAL,
)


def test_domain() -> None:
    """Test domain constant."""
    assert DOMAIN == "fglair_heatpump_controller"


def test_platforms() -> None:
    """Test platforms constant."""
    assert isinstance(PLATFORMS, list)
    assert "climate" in PLATFORMS


def test_default_values() -> None:
    """Test default values."""
    assert DEFAULT_TOKEN_PATH is not None
    assert isinstance(DEFAULT_TEMPERATURE_OFFSET, float)
    assert SCAN_INTERVAL is not None
    assert VERSION is not None


def test_version_type() -> None:
    """Test version is string."""
    assert isinstance(VERSION, str)


def test_all_constants_defined() -> None:
    """Test that all constants are defined and not None."""
    constants = [
        ATTRIBUTION,
        BINARY_SENSOR_DEVICE_CLASS,
        DEFAULT_MIN_STEP,
        DEFAULT_NAME,
        DEFAULT_TEMPERATURE_OFFSET,
        DEFAULT_TIMEOUT,
        DEFAULT_TOKEN_PATH,
        DOMAIN,
        DOMAIN_DATA,
        HORIZONTAL,
        ICON,
        ISSUE_URL,
        MAX_TEMP,
        MIN_TEMP,
        MIN_TIME_BETWEEN_UPDATES,
        NAME,
        PLATFORMS,
        REFRESH_MINUTES_INTERVAL,
        SCAN_INTERVAL,
        STARTUP_MESSAGE,
        VERSION,
        VERTICAL,
    ]

    for constant in constants:
        assert constant is not None


def test_domain_values() -> None:
    """Test domain-related constants."""
    assert DOMAIN == "fglair_heatpump_controller"
    assert DOMAIN_DATA == "fglair_heatpump_controller_data"
    assert DEFAULT_NAME == DOMAIN


def test_version_format() -> None:
    """Test version format."""
    assert isinstance(VERSION, str)
    assert len(VERSION) > 0
    # Version should be in format like "0.3.24"
    parts = VERSION.split(".")
    assert len(parts) == 3
    for part in parts:
        assert part.isdigit()


def test_temperature_constants() -> None:
    """Test temperature-related constants."""
    assert isinstance(MIN_TEMP, int)
    assert isinstance(MAX_TEMP, int)
    assert isinstance(DEFAULT_TEMPERATURE_OFFSET, float)
    assert isinstance(DEFAULT_MIN_STEP, float)

    assert MIN_TEMP < MAX_TEMP
    assert DEFAULT_TEMPERATURE_OFFSET >= 0
    assert DEFAULT_MIN_STEP > 0


def test_time_constants() -> None:
    """Test time-related constants."""
    assert isinstance(SCAN_INTERVAL, timedelta)
    assert isinstance(MIN_TIME_BETWEEN_UPDATES, timedelta)
    assert isinstance(REFRESH_MINUTES_INTERVAL, timedelta)
    assert isinstance(DEFAULT_TIMEOUT, int)

    assert SCAN_INTERVAL.total_seconds() > 0
    assert MIN_TIME_BETWEEN_UPDATES.total_seconds() > 0
    assert REFRESH_MINUTES_INTERVAL.total_seconds() > 0
    assert DEFAULT_TIMEOUT > 0


def test_platform_constants() -> None:
    """Test platform constants."""
    assert isinstance(PLATFORMS, list)
    assert len(PLATFORMS) > 0
    assert "climate" in PLATFORMS


def test_string_constants() -> None:
    """Test string constants."""
    assert isinstance(NAME, str)
    assert isinstance(ATTRIBUTION, str)
    assert isinstance(ISSUE_URL, str)
    assert isinstance(ICON, str)
    assert isinstance(BINARY_SENSOR_DEVICE_CLASS, str)
    assert isinstance(DEFAULT_TOKEN_PATH, str)
    assert isinstance(VERTICAL, str)
    assert isinstance(HORIZONTAL, str)

    assert len(NAME) > 0
    assert len(ATTRIBUTION) > 0
    assert len(ISSUE_URL) > 0
    assert len(ICON) > 0
    assert len(DEFAULT_TOKEN_PATH) > 0
    assert len(VERTICAL) > 0
    assert len(HORIZONTAL) > 0


def test_startup_message_content() -> None:
    """Test startup message content."""
    assert isinstance(STARTUP_MESSAGE, str)
    assert len(STARTUP_MESSAGE) > 0
    assert NAME in STARTUP_MESSAGE
    assert VERSION in STARTUP_MESSAGE
    assert ISSUE_URL in STARTUP_MESSAGE


def test_icon_format() -> None:
    """Test icon format."""
    assert ICON.startswith("mdi:")
    assert len(ICON) > 4


def test_issue_url_format() -> None:
    """Test issue URL format."""
    assert ISSUE_URL.startswith("https://")
    assert "github.com" in ISSUE_URL


def test_attribution_content() -> None:
    """Test attribution content."""
    assert "jsonplaceholder" in ATTRIBUTION.lower()


def test_vertical_horizontal_prefixes() -> None:
    """Test vertical and horizontal prefixes."""
    assert VERTICAL.endswith("_")
    assert HORIZONTAL.endswith("_")
    assert VERTICAL != HORIZONTAL


def test_constants_not_none() -> None:
    """Test that all constants are not None."""
    assert DOMAIN is not None
    assert NAME is not None
    assert VERSION is not None
    assert ICON is not None
    assert ISSUE_URL is not None
    assert STARTUP_MESSAGE is not None
    assert PLATFORMS is not None
    assert SCAN_INTERVAL is not None
    assert MIN_TEMP is not None
    assert MAX_TEMP is not None
    assert DEFAULT_TEMPERATURE_OFFSET is not None
    assert DEFAULT_TOKEN_PATH is not None


def test_constants_types() -> None:
    """Test that constants have correct types."""
    assert isinstance(DOMAIN, str)
    assert isinstance(NAME, str)
    assert isinstance(VERSION, str)
    assert isinstance(ICON, str)
    assert isinstance(ISSUE_URL, str)
    assert isinstance(STARTUP_MESSAGE, str)
    assert isinstance(PLATFORMS, list)
    assert isinstance(MIN_TEMP, int)
    assert isinstance(MAX_TEMP, int)
    assert isinstance(DEFAULT_TEMPERATURE_OFFSET, float)
    assert isinstance(DEFAULT_TOKEN_PATH, str)


def test_constants_values() -> None:
    """Test that constants have expected values."""
    assert DOMAIN == "fglair_heatpump_controller"
    assert "climate" in PLATFORMS
    assert MIN_TEMP < MAX_TEMP
    assert DEFAULT_TEMPERATURE_OFFSET >= 0
    assert ICON.startswith("mdi:")
    assert ISSUE_URL.startswith("https://")
    assert NAME in STARTUP_MESSAGE
    assert VERSION in STARTUP_MESSAGE


def test_constants_lengths() -> None:
    """Test that string constants have reasonable lengths."""
    assert len(DOMAIN) > 0
    assert len(NAME) > 0
    assert len(VERSION) > 0
    assert len(ICON) > 0
    assert len(ISSUE_URL) > 0
    assert len(STARTUP_MESSAGE) > 0
    assert len(DEFAULT_TOKEN_PATH) > 0


def test_platforms_list() -> None:
    """Test that platforms is a non-empty list."""
    assert isinstance(PLATFORMS, list)
    assert len(PLATFORMS) > 0
    assert "climate" in PLATFORMS


def test_scan_interval_properties() -> None:
    """Test scan interval properties."""
    assert SCAN_INTERVAL is not None
    assert hasattr(SCAN_INTERVAL, "total_seconds")
    assert SCAN_INTERVAL.total_seconds() > 0


def test_string_formatting() -> None:
    """Test string formatting in constants."""
    assert ICON.startswith("mdi:")
    assert ISSUE_URL.startswith("https://")
    assert "/" in ISSUE_URL or "." in ISSUE_URL


def test_domain_consistency() -> None:
    """Test domain consistency across constants."""
    assert DOMAIN == "fglair_heatpump_controller"
    assert DOMAIN in STARTUP_MESSAGE or NAME in STARTUP_MESSAGE
