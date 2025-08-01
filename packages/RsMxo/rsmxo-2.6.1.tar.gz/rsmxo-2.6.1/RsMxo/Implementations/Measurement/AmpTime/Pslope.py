from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PslopeCls:
	"""Pslope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pslope", core, parent)

	def set(self, pulses_slope: enums.PulseSlope, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:AMPTime:PSLope \n
		Snippet: driver.measurement.ampTime.pslope.set(pulses_slope = enums.PulseSlope.EITHer, measurement = repcap.Measurement.Default) \n
		Sets the first slope of the pulses to be counted. The setting is only relevant for pulse count measurement (method RsMxo.
		Measurement.Main.set is set to PULCnt. \n
			:param pulses_slope: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(pulses_slope, enums.PulseSlope)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:AMPTime:PSLope {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default) -> enums.PulseSlope:
		"""SCPI: MEASurement<*>:AMPTime:PSLope \n
		Snippet: value: enums.PulseSlope = driver.measurement.ampTime.pslope.get(measurement = repcap.Measurement.Default) \n
		Sets the first slope of the pulses to be counted. The setting is only relevant for pulse count measurement (method RsMxo.
		Measurement.Main.set is set to PULCnt. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: pulses_slope: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:AMPTime:PSLope?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
