from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActiveCls:
	"""Active commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("active", core, parent)

	def set(self, first: bool, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:ACTive \n
		Snippet: driver.measurement.active.set(first = False, measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param first: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(first)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:ACTive {param}')

	def get(self, measurement=repcap.Measurement.Default) -> bool:
		"""SCPI: MEASurement<*>:ACTive \n
		Snippet: value: bool = driver.measurement.active.get(measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: first: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:ACTive?')
		return Conversions.str_to_bool(response)
