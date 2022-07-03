import logging
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
import voluptuous as vol

from .api import PluggitVentilationApiClient
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL

_LOGGER: logging.Logger = logging.getLogger(__package__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class PluggitVentilationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            valid = self._test_network(host, port)
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_NAME] = DEFAULT_NAME
        user_input[CONF_HOST] = ""
        user_input[CONF_PORT] = DEFAULT_PORT
        user_input[CONF_SCAN_INTERVAL] = DEFAULT_SCAN_INTERVAL

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=user_input[CONF_NAME]): str,
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                    vol.Required(CONF_PORT, default=user_input[CONF_PORT]): int,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=user_input[CONF_SCAN_INTERVAL]
                    ): int,
                }
            ),
            errors=self._errors,
        )

    def _test_network(self, host, port):
        """Return true if credentials is valid."""
        try:
            client = PluggitVentilationApiClient(host, port)
            return client.test_connection()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Fatal error in main loop")
            pass
        return False


#    @staticmethod
#    @callback
#    def async_get_options_flow(config_entry):
#        return BlueprintOptionsFlowHandler(config_entry)
#
#    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
#        """Show the configuration form to edit location data."""
#        return self.async_show_form(
#            step_id="user",
#            data_schema=vol.Schema(
#                {
#                    vol.Required(CONFIG_IP, default=user_input[CONFIG_IP]): str,
#                }
#            ),
#            errors=self._errors,
#        )
#
#
#
# class BlueprintOptionsFlowHandler(config_entries.OptionsFlow):
#    """Blueprint config flow options handler."""
#
#    def __init__(self, config_entry):
#        """Initialize HACS options flow."""
#        self.config_entry = config_entry
#        self.options = dict(config_entry.options)
#
#    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
#        """Manage the options."""
#        return await self.async_step_user()
#
#    async def async_step_user(self, user_input=None):
#        """Handle a flow initialized by the user."""
#        if user_input is not None:
#            self.options.update(user_input)
#            return await self._update_options()
#
#        return self.async_show_form(
#            step_id="network",
#            data_schema=vol.Schema(
#                {
#                    vol.Required(x, default=self.options.get(x, True)): bool
#                    for x in sorted(PLATFORMS)
#                }
#            ),
#        )
#
#    async def _update_options(self):
#        """Update config entry options."""
#        return self.async_create_entry(
#            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
#        )
#
