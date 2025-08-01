from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AresetCls:
	"""Areset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("areset", core, parent)

	def set(self, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:STATistics:ARESet \n
		Snippet: driver.measurement.statistics.areset.set(measurement = repcap.Measurement.Default) \n
		Resets the statistics for all measurements. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:STATistics:ARESet')

	def set_and_wait(self, measurement=repcap.Measurement.Default, opc_timeout_ms: int = -1) -> None:
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		"""SCPI: MEASurement<*>:STATistics:ARESet \n
		Snippet: driver.measurement.statistics.areset.set_with_opc(measurement = repcap.Measurement.Default) \n
		Resets the statistics for all measurements. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MEASurement{measurement_cmd_val}:STATistics:ARESet', opc_timeout_ms)
