"""Parent component for Energenie TRV devices.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/energenie/
"""

import logging

import voluptuous as vol
from pymihome import Connection, EnergenieTemperature
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_DEVICES

REQUIREMENTS = ['pymihome==0.0.6']

_LOGGER = logging.getLogger(__name__)

DOMAIN = "energenie"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_DEVICES, default=[]):
            vol.All(cv.ensure_list, [dict]),
    })
}, extra=vol.ALLOW_EXTRA)
#
ENERGENIE_DEVICES = "energenie_devices"
#
#
def setup(hass, config):
    """Set up the Dyson parent component."""
    _LOGGER.info("Creating new Dyson component")

    if ENERGENIE_DEVICES not in hass.data:
        hass.data[ENERGENIE_DEVICES] = []


    mihome = Connection(config[DOMAIN].get(CONF_USERNAME), config[DOMAIN].get(CONF_PASSWORD))

    if not mihome:
        _LOGGER.error("Not connected to Energenie account. Unable to add devices")
        return False

    _LOGGER.info("Connected to Energenie account")
    energenie_devices = mihome.subdevices
    if CONF_DEVICES in config[DOMAIN] and config[DOMAIN].get(CONF_DEVICES):
        configured_devices = config[DOMAIN].get(CONF_DEVICES)
        for device in configured_devices:
            energenie_device = next((d for d in energenie_devices if
                                 d.id == device["id"]), None)
            if energenie_device:
                try:
                    _LOGGER.info("Found Energenie device=%s", energenie_device)
                    hass.data[ENERGENIE_DEVICES].append(EnergenieTemperature(mihome, energenie_device))
                except OSError as ose:
                    _LOGGER.error("Unable to add device %s: %s",
                                  str(energenie_device['id']), str(ose))
            else:
                _LOGGER.warning(
                    "Unable to find device=%s",
                    device["id"])
    else:
        for device in energenie_devices:
            _LOGGER.info("Connected to device %s", device)
            hass.data[ENERGENIE_DEVICES].append(EnergenieTemperature(mihome, device))
    # Start fan/sensors components
    if hass.data[ENERGENIE_DEVICES]:
        _LOGGER.debug("Starting sensor components")
        discovery.load_platform(hass, "sensor", DOMAIN, {}, config)
        discovery.load_platform(hass, "climate", DOMAIN, {}, config)
        #def load_platform(hass, component, platform, discovered, hass_config)


    return True
