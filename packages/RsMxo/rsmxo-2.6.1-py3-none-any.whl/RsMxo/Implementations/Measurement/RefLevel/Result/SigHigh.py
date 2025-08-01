from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SigHighCls:
	"""SigHigh commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sigHigh", core, parent)

	def get(self, measurement=repcap.Measurement.Default, refLevel=repcap.RefLevel.Default) -> float:
		"""SCPI: MEASurement<*>:REFLevel<*>:RESult:SIGHigh \n
		Snippet: value: float = driver.measurement.refLevel.result.sigHigh.get(measurement = repcap.Measurement.Default, refLevel = repcap.RefLevel.Default) \n
		Return the high and low signal level, respectively. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: signal_high: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:REFLevel{refLevel_cmd_val}:RESult:SIGHigh?')
		return Conversions.str_to_float(response)
