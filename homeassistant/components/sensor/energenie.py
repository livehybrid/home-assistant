"""
Support for Adafruit DHT temperature and humidity sensor.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.dht/
"""
from homeassistant.components.energenie import ENERGENIE_DEVICES
from homeassistant.const import TEMP_CELSIUS, PRECISION_WHOLE
from pymihome import EnergenieTemperature, Connection # pylint: disable=import-error
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD


import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    TEMP_FAHRENHEIT, CONF_NAME, CONF_MONITORED_CONDITIONS)
from homeassistant.helpers.entity import Entity
from homeassistant.util.temperature import celsius_to_fahrenheit

REQUIREMENTS = ['pymihome==0.0.6']

_LOGGER = logging.getLogger(__name__)

CONF_ID = 'id'
DEFAULT_NAME = 'trv'
DOMAIN = 'energenie'

SENSOR_TEMPERATURE = 'temperature'
SENSOR_TYPES = {
    SENSOR_TEMPERATURE: ['Temperature', 'C']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    #vol.Required(CONF_ID): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]): vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Energenie TRV sensor."""
    devices = []
    name = config.get(CONF_NAME)
    from pprint import pprint
    for device in [d for d in hass.data[ENERGENIE_DEVICES] if
                   isinstance(d, EnergenieTemperature)]:
        devices.append(EnergenieTemperatureSensor(device))
    add_entities(devices)

class EnergenieTemperatureSensor(Entity):
    """Implementation of the Energenie TRV."""

    def __init__(self,device):
        """Initialize the sensor."""
        self.client_name = device.name
        self.device = device
        self.temp_unit = TEMP_CELSIUS
        self.type = "target"
        self._name = self.type
        self._state = None
        self._unit_of_measurement = self.unit_of_measurement


    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self.client_name, self._name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def precision(self):
        return PRECISION_WHOLE

    def update(self):
        #self.type ?
        """Get the latest data from the Energenie API and updates the states."""
        self.device.getinfo()
        if self.type == "latest":
            temperature = self.device.latest_temp
        else:
            temperature = self.device.target_temp
        self._state = round(temperature, 1)
        if self.temp_unit == TEMP_FAHRENHEIT:
            self._state = round(celsius_to_fahrenheit(temperature), 1)
