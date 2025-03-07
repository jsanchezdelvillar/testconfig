from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, CONF_POINT_ID_LIST

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor platform from a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]
    point_id_list = entry.data.get(CONF_POINT_ID_LIST, [])
    sensor_names = entry.data.get("sensor_names", {})
    
    sensors = [SolarSensor(api, point_id, sensor_names.get(point_id, f"Sensor {point_id}")) for point_id in point_id_list]
    async_add_entities(sensors, True)

class SolarSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, api, point_id, name):
        """Initialize the sensor."""
        self.api = api
        self._point_id = point_id
        self._attr_name = name
        self._attr_unique_id = f"solar_sensor_{point_id}"
        self._state = None
        _LOGGER.debug("Sensor %s initialized with value none", name)

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("Getting state for sensor %s: %s", self._name, self._state)
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        data = await self.api.get_device_data()
        if data:
            values = data.get("data", {})
            self._state = values.get(self._point_id, 0)
        else:
            _LOGGER.warning("Failed to update sensor data")
