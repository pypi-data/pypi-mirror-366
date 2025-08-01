from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get(self, measurement=repcap.Measurement.Default) -> int:
		"""SCPI: MEASurement<*>:RESult:EVENts:COUNt \n
		Snippet: value: int = driver.measurement.result.events.count.get(measurement = repcap.Measurement.Default) \n
		Returns the number of measured events in one acquisition. The command is relevant for measurements of all events, see
		method RsMxo.Measurement.Multiple.set. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: count: Number of events"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:RESult:EVENts:COUNt?')
		return Conversions.str_to_int(response)
