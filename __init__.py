import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the integration from configuration.yaml."""
    _LOGGER.debug("async_setup called with config: %s", config)
    hass.data.setdefault(DOMAIN, {})

    async def handle_get_sensor_data(call):
        """Handle the service call to get sensor data."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            sensors = entry_data.get("sensors", {})
            for sensor in sensors.values():
                await sensor.async_update_ha_state()

    async def handle_update_token(call):
        """Handle the service call to update the authentication token."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if "update_token" in entry_data:
                await entry_data["update_token"]()

    hass.services.async_register(DOMAIN, "get_sensor_data", handle_get_sensor_data)
    hass.services.async_register(DOMAIN, "update_token", handle_update_token)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a config entry."""
    _LOGGER.debug("async_setup_entry called with entry: %s", entry.data)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload an integration entry."""
    _LOGGER.debug("async_unload_entry called for entry: %s", entry.entry_id)
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
