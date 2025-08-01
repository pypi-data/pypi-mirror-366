from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StopCls:
	"""Stop commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stop", core, parent)

	def get(self, measurement=repcap.Measurement.Default) -> float:
		"""SCPI: MEASurement<*>:RESult:STOP \n
		Snippet: value: float = driver.measurement.result.stop.get(measurement = repcap.Measurement.Default) \n
		Return the start and stop times of the specified measurement. The parameter defines the measurement. If no parameter is
		specified, the result of the main measurement is returned. The main measurement is defined using method RsMxo.Measurement.
		Main.set. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: stop: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:RESult:STOP?')
		return Conversions.str_to_float(response)
