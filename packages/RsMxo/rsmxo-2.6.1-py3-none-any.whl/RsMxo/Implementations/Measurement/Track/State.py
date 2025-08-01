from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:TRACk[:STATe] \n
		Snippet: driver.measurement.track.state.set(state = False, measurement = repcap.Measurement.Default) \n
		Enables or disables the track for the selected measurement. \n
			:param state: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(state)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:TRACk:STATe {param}')

	def get(self, measurement=repcap.Measurement.Default) -> bool:
		"""SCPI: MEASurement<*>:TRACk[:STATe] \n
		Snippet: value: bool = driver.measurement.track.state.get(measurement = repcap.Measurement.Default) \n
		Enables or disables the track for the selected measurement. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: state: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:TRACk:STATe?')
		return Conversions.str_to_bool(response)
