from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PolarityCls:
	"""Polarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polarity", core, parent)

	def set(self, polarity: enums.PulseSlope, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:JITTer:POLarity \n
		Snippet: driver.measurement.jitter.polarity.set(polarity = enums.PulseSlope.EITHer, measurement = repcap.Measurement.Default) \n
		For cycle-cycle width and the cycle-cycle duty cycle measurements, the command sets the polarity of pulses for which the
		pulse width is measured: POSitive or NEGative. method RsMxo.Measurement.Main.set is set to measurements CCWidth |
		CCDutycycle. For skew delay and skew phase measurements, the command sets the edge of the first waveform from which the
		measurements starts: POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is set to measurements SKWDelay |
		SKWPhase. \n
			:param polarity: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(polarity, enums.PulseSlope)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:JITTer:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default) -> enums.PulseSlope:
		"""SCPI: MEASurement<*>:JITTer:POLarity \n
		Snippet: value: enums.PulseSlope = driver.measurement.jitter.polarity.get(measurement = repcap.Measurement.Default) \n
		For cycle-cycle width and the cycle-cycle duty cycle measurements, the command sets the polarity of pulses for which the
		pulse width is measured: POSitive or NEGative. method RsMxo.Measurement.Main.set is set to measurements CCWidth |
		CCDutycycle. For skew delay and skew phase measurements, the command sets the edge of the first waveform from which the
		measurements starts: POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is set to measurements SKWDelay |
		SKWPhase. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: polarity: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:JITTer:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
