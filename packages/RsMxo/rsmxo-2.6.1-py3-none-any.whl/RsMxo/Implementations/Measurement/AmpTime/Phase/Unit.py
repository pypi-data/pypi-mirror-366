from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UnitCls:
	"""Unit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("unit", core, parent)

	def set(self, phase_mode: enums.PhaseMode, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:AMPTime:PHASe:UNIT \n
		Snippet: driver.measurement.ampTime.phase.unit.set(phase_mode = enums.PhaseMode.DEGRees, measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param phase_mode: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(phase_mode, enums.PhaseMode)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:AMPTime:PHASe:UNIT {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default) -> enums.PhaseMode:
		"""SCPI: MEASurement<*>:AMPTime:PHASe:UNIT \n
		Snippet: value: enums.PhaseMode = driver.measurement.ampTime.phase.unit.get(measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: phase_mode: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:AMPTime:PHASe:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.PhaseMode)
