from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Fd2ValueCls:
	"""Fd2Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fd2Value", core, parent)

	def set(self, field_2_value: List[int], measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:PROTocol:FD2Value \n
		Snippet: driver.measurement.protocol.fd2Value.set(field_2_value = [1, 2, 3], measurement = repcap.Measurement.Default) \n
		Sets or queries the one or more values of the field, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param field_2_value: List of comma separated values
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.list_to_csv_str(field_2_value)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:PROTocol:FD2Value {param}')

	def get(self, measurement=repcap.Measurement.Default) -> List[int]:
		"""SCPI: MEASurement<*>:PROTocol:FD2Value \n
		Snippet: value: List[int] = driver.measurement.protocol.fd2Value.get(measurement = repcap.Measurement.Default) \n
		Sets or queries the one or more values of the field, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: field_2_value: List of comma separated values"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_bin_or_ascii_int_list(f'MEASurement{measurement_cmd_val}:PROTocol:FD2Value?')
		return response
