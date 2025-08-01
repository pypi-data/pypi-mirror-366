from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultsCls:
	"""Results commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("results", core, parent)

	def set(self, disp_res_lines: bool, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:DISPlay:RESults \n
		Snippet: driver.measurement.display.results.set(disp_res_lines = False, measurement = repcap.Measurement.Default) \n
		Enables the measurement annotations for the selected measurement. These annotations are, for example, periods, maximum
		and minimum values, relevant reference levels, and more. \n
			:param disp_res_lines: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(disp_res_lines)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:DISPlay:RESults {param}')

	def get(self, measurement=repcap.Measurement.Default) -> bool:
		"""SCPI: MEASurement<*>:DISPlay:RESults \n
		Snippet: value: bool = driver.measurement.display.results.get(measurement = repcap.Measurement.Default) \n
		Enables the measurement annotations for the selected measurement. These annotations are, for example, periods, maximum
		and minimum values, relevant reference levels, and more. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: disp_res_lines: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:DISPlay:RESults?')
		return Conversions.str_to_bool(response)
