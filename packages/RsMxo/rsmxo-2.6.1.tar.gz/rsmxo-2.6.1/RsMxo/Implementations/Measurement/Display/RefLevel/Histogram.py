from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HistogramCls:
	"""Histogram commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("histogram", core, parent)

	def set(self, disp_histg: bool, measurement=repcap.Measurement.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""SCPI: MEASurement<*>:DISPlay:REFLevel<*>:HISTogram \n
		Snippet: driver.measurement.display.refLevel.histogram.set(disp_histg = False, measurement = repcap.Measurement.Default, refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param disp_histg: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.bool_to_str(disp_histg)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:DISPlay:REFLevel{refLevel_cmd_val}:HISTogram {param}')

	def get(self, measurement=repcap.Measurement.Default, refLevel=repcap.RefLevel.Default) -> bool:
		"""SCPI: MEASurement<*>:DISPlay:REFLevel<*>:HISTogram \n
		Snippet: value: bool = driver.measurement.display.refLevel.histogram.get(measurement = repcap.Measurement.Default, refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: disp_histg: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:DISPlay:REFLevel{refLevel_cmd_val}:HISTogram?')
		return Conversions.str_to_bool(response)
