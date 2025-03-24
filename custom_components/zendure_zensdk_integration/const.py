"""Constants for Zendure ZenSDK Integration."""
# Base component constants
NAME = "Zendure ZenSDK Integration"
DOMAIN = "zendure_zensdk_integration"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/flattman/zendure-zensdk-integration/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Configuration and options
CONF_SERIAL_NUMBER = "serial_number"
CONF_MODEL = "model"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_UPDATE_INTERVAL = 30  # Standardmäßiges Update-Intervall in Sekunden
MIN_UPDATE_INTERVAL = 10
MAX_UPDATE_INTERVAL = 600

MODEL_SOLARFLOW800 = "SolarFlow800"
SUPPORTED_MODELS = [MODEL_SOLARFLOW800]

DEVICE_MANUFACTURER = "Zendure"

DATA_KEY = DOMAIN

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
