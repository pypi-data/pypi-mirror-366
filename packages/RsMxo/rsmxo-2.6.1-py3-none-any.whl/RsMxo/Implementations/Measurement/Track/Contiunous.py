from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ContiunousCls:
	"""Contiunous commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("contiunous", core, parent)

	def set(self, auto_scl_enable: bool, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:TRACk:CONTiunous \n
		Snippet: driver.measurement.track.contiunous.set(auto_scl_enable = False, measurement = repcap.Measurement.Default) \n
		Performs an automatic scaling whenever the track does not fit in the diagram during the measurement period. \n
			:param auto_scl_enable: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(auto_scl_enable)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:TRACk:CONTiunous {param}')

	def get(self, measurement=repcap.Measurement.Default) -> bool:
		"""SCPI: MEASurement<*>:TRACk:CONTiunous \n
		Snippet: value: bool = driver.measurement.track.contiunous.get(measurement = repcap.Measurement.Default) \n
		Performs an automatic scaling whenever the track does not fit in the diagram during the measurement period. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: auto_scl_enable: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:TRACk:CONTiunous?')
		return Conversions.str_to_bool(response)
