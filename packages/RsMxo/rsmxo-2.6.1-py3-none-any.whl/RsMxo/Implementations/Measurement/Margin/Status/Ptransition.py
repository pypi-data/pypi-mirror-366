from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PtransitionCls:
	"""Ptransition commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ptransition", core, parent)

	def set(self, value: bool, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:MARGin:STATus:PTRansition \n
		Snippet: driver.measurement.margin.status.ptransition.set(value = False, measurement = repcap.Measurement.Default) \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param value: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(value)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:MARGin:STATus:PTRansition {param}')

	def get(self, measurement=repcap.Measurement.Default) -> bool:
		"""SCPI: MEASurement<*>:MARGin:STATus:PTRansition \n
		Snippet: value: bool = driver.measurement.margin.status.ptransition.get(measurement = repcap.Measurement.Default) \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: value: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:MARGin:STATus:PTRansition?')
		return Conversions.str_to_bool(response)
