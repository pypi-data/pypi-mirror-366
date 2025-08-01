from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GateCls:
	"""Gate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gate", core, parent)

	def set(self, gate: int, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:GATE \n
		Snippet: driver.measurement.gate.set(gate = 1, measurement = repcap.Measurement.Default) \n
		Sets the gate of the indicated measurement. Enable a gate before you assign a measurement to it (method RsMxo.Gate.Enable.
		set =ON) . The query returns 0, if no gate is assigned. \n
			:param gate: Number of the gate to be used
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(gate)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:GATE {param}')

	def get(self, measurement=repcap.Measurement.Default) -> int:
		"""SCPI: MEASurement<*>:GATE \n
		Snippet: value: int = driver.measurement.gate.get(measurement = repcap.Measurement.Default) \n
		Sets the gate of the indicated measurement. Enable a gate before you assign a measurement to it (method RsMxo.Gate.Enable.
		set =ON) . The query returns 0, if no gate is assigned. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: gate: Number of the gate to be used"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:GATE?')
		return Conversions.str_to_int(response)
