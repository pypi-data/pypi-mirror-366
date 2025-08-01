from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Fd2NameCls:
	"""Fd2Name commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fd2Name", core, parent)

	def set(self, field_2_name: str, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:PROTocol:FD2Name \n
		Snippet: driver.measurement.protocol.fd2Name.set(field_2_name = 'abc', measurement = repcap.Measurement.Default) \n
		Sets or queries the name of the field or the field type, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param field_2_name: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.value_to_quoted_str(field_2_name)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:PROTocol:FD2Name {param}')

	def get(self, measurement=repcap.Measurement.Default) -> str:
		"""SCPI: MEASurement<*>:PROTocol:FD2Name \n
		Snippet: value: str = driver.measurement.protocol.fd2Name.get(measurement = repcap.Measurement.Default) \n
		Sets or queries the name of the field or the field type, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: field_2_name: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:PROTocol:FD2Name?')
		return trim_str_response(response)
