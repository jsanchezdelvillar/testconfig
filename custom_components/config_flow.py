import logging
import voluptuous as vol
import yaml
import os
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_APPKEY, CONF_X_ACCESS_KEY, CONF_PUBLIC_KEY, CONF_PS_KEY, CONF_POINT_ID_LIST

_LOGGER = logging.getLogger(__name__)

def read_secrets():
    secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'secrets.yaml')
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as file:
            return yaml.safe_load(file)
    return {}

secrets = read_secrets()

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME, default=secrets.get(CONF_USERNAME, '')): str,
    vol.Required(CONF_PASSWORD, default=secrets.get(CONF_PASSWORD, '')): str,
    vol.Required(CONF_APPKEY, default=secrets.get(CONF_APPKEY, '')): str,
    vol.Required(CONF_X_ACCESS_KEY, default=secrets.get(CONF_X_ACCESS_KEY, '')): str,
    vol.Required(CONF_PUBLIC_KEY, default=secrets.get(CONF_PUBLIC_KEY, '')): str,
    vol.Required(CONF_PS_KEY, default=secrets.get(CONF_PS_KEY, '')): str,
    vol.Required(CONF_POINT_ID_LIST, default=secrets.get(CONF_POINT_ID_LIST, [])): [str],
    vol.Optional("sensor_names", default=secrets.get("sensor_names", {})): vol.Schema({str: str})
})

class CustomSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Custom Solar."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        _LOGGER.debug("async_step_user called with input: %s", user_input)

        if user_input is not None:
            try:
                _LOGGER.debug("Creating entry with data: %s", user_input)
                self.update_secrets(user_input)
                return self.async_create_entry(title="Custom Solar", data=user_input)
            except Exception as e:
                _LOGGER.error("Error creating entry: %s", e)
                errors["base"] = "cannot_create_entry"
        
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    def update_secrets(self, user_input):
        secrets = read_secrets()
        secrets.update(user_input)
        secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'secrets.yaml')
        with open(secrets_path, 'w') as file:
            yaml.safe_dump(secrets, file)

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        _LOGGER.debug("async_get_options_flow called for entry: %s", entry.data)
        return OptionsFlowHandler(entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, entry):
        """Initialize options flow."""
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))
