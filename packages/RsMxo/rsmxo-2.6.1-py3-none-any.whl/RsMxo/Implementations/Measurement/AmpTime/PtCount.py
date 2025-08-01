from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PtCountCls:
	"""PtCount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ptCount", core, parent)

	def set(self, pulse_count: int, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:AMPTime:PTCount \n
		Snippet: driver.measurement.ampTime.ptCount.set(pulse_count = 1, measurement = repcap.Measurement.Default) \n
		Sets the number of positive pulses for the pulse train measurement. It measures the duration of N positive pulses from
		the rising edge of the first pulse to the falling edge of the N-th pulse. \n
			:param pulse_count: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(pulse_count)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:AMPTime:PTCount {param}')

	def get(self, measurement=repcap.Measurement.Default) -> int:
		"""SCPI: MEASurement<*>:AMPTime:PTCount \n
		Snippet: value: int = driver.measurement.ampTime.ptCount.get(measurement = repcap.Measurement.Default) \n
		Sets the number of positive pulses for the pulse train measurement. It measures the duration of N positive pulses from
		the rising edge of the first pulse to the falling edge of the N-th pulse. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: pulse_count: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:AMPTime:PTCount?')
		return Conversions.str_to_int(response)
