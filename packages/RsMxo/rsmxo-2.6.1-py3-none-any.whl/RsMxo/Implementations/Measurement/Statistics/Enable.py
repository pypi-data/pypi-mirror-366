from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, global_statistics_enable: bool, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:STATistics[:ENABle] \n
		Snippet: driver.measurement.statistics.enable.set(global_statistics_enable = False, measurement = repcap.Measurement.Default) \n
		Enables statistics calculation for all measurements. \n
			:param global_statistics_enable: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(global_statistics_enable)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:STATistics:ENABle {param}')

	def get(self, measurement=repcap.Measurement.Default) -> bool:
		"""SCPI: MEASurement<*>:STATistics[:ENABle] \n
		Snippet: value: bool = driver.measurement.statistics.enable.get(measurement = repcap.Measurement.Default) \n
		Enables statistics calculation for all measurements. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: global_statistics_enable: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:STATistics:ENABle?')
		return Conversions.str_to_bool(response)
