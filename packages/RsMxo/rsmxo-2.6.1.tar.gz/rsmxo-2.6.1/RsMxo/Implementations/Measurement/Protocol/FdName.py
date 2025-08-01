from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FdNameCls:
	"""FdName commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fdName", core, parent)

	def set(self, field_name: str, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:PROTocol:FDName \n
		Snippet: driver.measurement.protocol.fdName.set(field_name = 'abc', measurement = repcap.Measurement.Default) \n
		Sets or queries the name of the field or the field type, at which the oscilloscope executes or starts the measurement. \n
			:param field_name: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.value_to_quoted_str(field_name)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:PROTocol:FDName {param}')

	def get(self, measurement=repcap.Measurement.Default) -> str:
		"""SCPI: MEASurement<*>:PROTocol:FDName \n
		Snippet: value: str = driver.measurement.protocol.fdName.get(measurement = repcap.Measurement.Default) \n
		Sets or queries the name of the field or the field type, at which the oscilloscope executes or starts the measurement. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: field_name: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:PROTocol:FDName?')
		return trim_str_response(response)
