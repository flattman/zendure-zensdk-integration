"""Adds config flow for Zendure ZenSDK Integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import ZendureZensdkIntegrationApiClient
from .const import (
    CONF_MODEL,
    CONF_SERIAL_NUMBER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    MODEL_SOLARFLOW800,
    SUPPORTED_MODELS,
    PLATFORMS
)


class ZendureZensdkIntegrationFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for zendure_zensdk_integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_step_model(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_SERIAL_NUMBER): str}
            ),
            errors=self._errors,
        )
    
    async def async_step_model(self, user_input=None):
        """Handle den Modell-Auswahl Schritt."""
        self._async_current_entries()

        if user_input is not None:
            user_input[CONF_MODEL] = MODEL_SOLARFLOW800  # Aktuell nur ein Modell
            self.serial_number = user_input[CONF_SERIAL_NUMBER]
            return await self.async_step_update_interval()

        return self.async_show_form(
            step_id="model",
            data_schema=vol.Schema(
                {vol.Required(CONF_MODEL, default=MODEL_SOLARFLOW800): vol.In(SUPPORTED_MODELS)}
            ),
            errors=self._errors,
        )

    async def async_step_update_interval(self, user_input=None):
        """Handle den Update-Intervall Schritt."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"{MODEL_SOLARFLOW800} ({self.serial_number[-4:]})",
                data={CONF_SERIAL_NUMBER: self.serial_number, CONF_MODEL: MODEL_SOLARFLOW800},
                options={CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL]},
            )

        return self.async_show_form(
            step_id="update_interval",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                    )
                }
            ),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ZendureZensdkIntegrationOptionsFlowHandler(config_entry)


class ZendureZensdkIntegrationOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for zendure_zensdk_integration."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Handle den ersten Schritt des Optionen-Flusses."""
        return await self.async_step_options(user_input)
    
    async def async_step_options(self, user_input: dict[str, Any] = None):
        """Handle das Einstellen der Optionen."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_SERIAL_NUMBER), data=self.options
        )
