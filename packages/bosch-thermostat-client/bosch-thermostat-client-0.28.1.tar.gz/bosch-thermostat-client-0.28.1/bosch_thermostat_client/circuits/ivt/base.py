"""IVT Circuit."""
import logging

from ..circuit import CircuitWithSchedule
from bosch_thermostat_client.const import (
    HVAC_ACTION,
    HVAC_HEAT,
    HVAC_OFF,
    STATUS,
    MIN_VALUE,
    MAX_VALUE,
    ACTIVE_PROGRAM,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    MIN_REF,
    MAX_REF,
    RESULT,
    VALUE,
    URI,
    HA_NAME,
    BOSCH_NAME,
    REFERENCES,
    SWITCH_PROGRAMS,
    ID,
    WRITEABLE,
)
from bosch_thermostat_client.const.ivt import (
    CURRENT_SETPOINT,
    CAN,
    ALLOWED_VALUES,
    CIRCUIT_TYPES,
)

_LOGGER = logging.getLogger(__name__)


class IVTCircuit(CircuitWithSchedule):
    def __init__(self, connector, attr_id, db, _type, bus_type, current_date, **kwargs):
        super().__init__(
            connector, attr_id, db, CIRCUIT_TYPES[_type], bus_type, current_date
        )

    @property
    def support_presets(self):
        if self._op_mode.is_auto:
            return True
        return False

    @property
    def state(self):
        """Retrieve state of the circuit."""
        if self._state:
            state = self.get_value(STATUS)
            if state:
                return state
            if self._bus_type == CAN:
                if self.get_value(CURRENT_SETPOINT):
                    return True

    @property
    def hvac_action(self):
        """For IVT is probably the best to check pumpModulation."""
        hvac_uri = self._db.get(HVAC_ACTION)
        if self.target_temperature == 0:
            return HVAC_OFF
        if hvac_uri:
            hv_value = int(self.get_value(hvac_uri, -1))
            if hv_value == 0:
                return HVAC_OFF
            elif hv_value > 0:
                return HVAC_HEAT

    @property
    def min_temp(self):
        """Retrieve minimum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MIN_TEMP
        else:
            setpoint_min = self.get_property(self._temp_setpoint).get(
                MIN_VALUE, self.get_value(self._db[MIN_REF], False)
            )
            min_temp = self.schedule.get_min_temp_for_mode(setpoint_min)
            if min_temp == ACTIVE_PROGRAM:
                min_temp = self.get_value_from_active_setpoint(MIN_VALUE)
            return min_temp

    @property
    def max_temp(self):
        """Retrieve maximum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MAX_TEMP
        else:
            setpoint_max = self.get_property(self._temp_setpoint).get(
                MAX_VALUE, self.get_value(self._db[MAX_REF], False)
            )
            max_temp = self.schedule.get_max_temp_for_mode(setpoint_max)
            if max_temp == ACTIVE_PROGRAM:
                max_temp = self.get_value_from_active_setpoint(MAX_VALUE)
            return max_temp

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        active_program_not_in_schedule = False
        if self._op_mode.is_off:
            return False
        if target_temp == temperature:
            _LOGGER.debug("Temperature is the same as already set. Exiting")
            return True
        if self.min_temp < temperature < self.max_temp and target_temp != temperature:
            target_uri = None
            if self._temp_setpoint:
                target_uri = self._data[self._temp_setpoint][URI]
            elif self._op_mode.is_auto:
                target_uri = self.schedule.get_uri_setpoint_for_current_mode()
                if target_uri == ACTIVE_PROGRAM:
                    active_program_not_in_schedule = True
                    target_uri = self._data[self.active_program_setpoint][URI]
            if not target_uri:
                _LOGGER.debug("Not setting temp. Don't know how")
                return False
            result = await self._connector.put(target_uri, temperature)
            _LOGGER.debug("Set temperature for %s with result %s", self.name, result)
            if result:
                if self._temp_setpoint:
                    self._data[self._temp_setpoint][RESULT][VALUE] = temperature
                elif not active_program_not_in_schedule and self.schedule:
                    self.schedule.cache_temp_for_mode(temperature)
                return True
        _LOGGER.error(
            "Setting temperature not allowed in this mode. Temperature is probably out of range MIN-MAX!"
        )
        return False

    @property
    def ha_modes(self):
        """Retrieve HA modes."""
        return [
            v[HA_NAME]
            for v in self._hastates
            if any(x in self._op_mode.available_modes for x in v[BOSCH_NAME])
        ]

    @property
    def preset_modes(self):
        active_programs = self.get_property(ACTIVE_PROGRAM).get(ALLOWED_VALUES, [])
        if active_programs:
            return active_programs
        result = self.get_property(SWITCH_PROGRAMS)
        return [result[REFERENCES][0][ID].split("/")[-1]]

    @property
    def preset_mode(self):
        return self.get_activeswitchprogram()

    async def set_preset_mode(self, preset_mode):
        act_program = self._data.get(ACTIVE_PROGRAM, {})
        active_program_uri = act_program[URI]
        active_program = act_program.get(RESULT, {})
        allowed_presets = active_program.get(ALLOWED_VALUES, [])
        if (
            preset_mode in allowed_presets
            and active_program.get(WRITEABLE, False)
            and active_program.get(VALUE) != preset_mode
        ):
            result = await self._connector.put(active_program_uri, preset_mode)
            await self.update_requested_key(ACTIVE_PROGRAM)
            new_program = self.get_activeswitchprogram()
            await self._schedule.update_schedule(new_program)
            return result
