from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NcyclesCls:
	"""Ncycles commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ncycles", core, parent)

	def set(self, number_cycles: int, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:JITTer:NCYCles \n
		Snippet: driver.measurement.jitter.ncycles.set(number_cycles = 1, measurement = repcap.Measurement.Default) \n
		Sets the number of periods (cycles) that are accumulated to measure the N-cycle jitter. \n
			:param number_cycles: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(number_cycles)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:JITTer:NCYCles {param}')

	def get(self, measurement=repcap.Measurement.Default) -> int:
		"""SCPI: MEASurement<*>:JITTer:NCYCles \n
		Snippet: value: int = driver.measurement.jitter.ncycles.get(measurement = repcap.Measurement.Default) \n
		Sets the number of periods (cycles) that are accumulated to measure the N-cycle jitter. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: number_cycles: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:JITTer:NCYCles?')
		return Conversions.str_to_int(response)
