"""
Support for Energenie TRV.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/climate.energenie/
"""
import logging

from homeassistant.components.energenie import ENERGENIE_DEVICES
from homeassistant.util.temperature import celsius_to_fahrenheit

from homeassistant.components.climate import (
    ClimateDevice, STATE_IDLE,
    SUPPORT_TARGET_TEMPERATURE)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT, ATTR_TEMPERATURE, PRECISION_WHOLE

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['pymihome==0.0.6']

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Energenie TRV components."""
    if discovery_info is None:
        return

    from pymihome import Connection, EnergenieTemperature
    # Get Energenie Devices from parent component.
    add_devices(
        [EnergenieClimateDevice(device)
         for device in hass.data[ENERGENIE_DEVICES]
         if isinstance(device, EnergenieTemperature)]
    )


class EnergenieClimateDevice(ClimateDevice):
    """Representation of an Energenie TRV."""

    def __init__(self, device):
        """Initialize the TRV."""
        self.device = device
        self._current_temp = None

        """Initialize the sensor."""
        self.client_name = device.name
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


    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        # self.hass.async_add_job(self.device.add_message_listener,
        #                         self.on_message)

    def on_message(self, message):
        """Call when new messages received from the climate."""
        from pymihome import Connection, EnergenieTemperature

        _LOGGER.debug("Message received for climate device %s : %s",
                      self.name, message)
        self.schedule_update_ha_state()

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

    @property
    def should_poll(self):
        return True

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self):
        """Return the display name of this climate."""
        return self.device.name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def precision(self):
        return PRECISION_WHOLE

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.device.latest_temp

    @property
    def target_temperature(self):
        """Return the target temperature."""
        return self.device.target_temp


    @property
    def current_operation(self):
        return STATE_IDLE

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return [STATE_IDLE]

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return
        target_temp = int(target_temp)
        _LOGGER.info("Set %s temperature %s", self.name, target_temp)

        target_temp = min(self.max_temp, target_temp)
        target_temp = max(self.min_temp, target_temp)
        self.device.set_temp(target_temp)

        # from libpurecoollink.const import HeatTarget, HeatMode
        # self._device.set_configuration(
        #     heat_target=HeatTarget.celsius(target_temp),
        #     heat_mode=HeatMode.HEAT_ON)

    # def set_operation_mode(self, operation_mode):
    #     """Set operation mode."""
    #     _LOGGER.debug("Set %s heat mode %s", self.name, operation_mode)
    #     from libpurecoollink.const import HeatMode
    #     if operation_mode == STATE_HEAT:
    #         self._device.set_configuration(heat_mode=HeatMode.HEAT_ON)
    #     elif operation_mode == STATE_COOL:
    #         self._device.set_configuration(heat_mode=HeatMode.HEAT_OFF)

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 4

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 30
