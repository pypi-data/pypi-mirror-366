from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OffsetCls:
	"""Offset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	def set(self, vertical_offset: float, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:TRACk:OFFSet \n
		Snippet: driver.measurement.track.offset.set(vertical_offset = 1.0, measurement = repcap.Measurement.Default) \n
		Sets or queries the offset of the track waveform. If method RsMxo.Measurement.Track.Contiunous.set is ON, use the command
		to query the current value. If method RsMxo.Measurement.Track.Contiunous.set is OFF, the command sets the offset. \n
			:param vertical_offset: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(vertical_offset)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:TRACk:OFFSet {param}')

	def get(self, measurement=repcap.Measurement.Default) -> float:
		"""SCPI: MEASurement<*>:TRACk:OFFSet \n
		Snippet: value: float = driver.measurement.track.offset.get(measurement = repcap.Measurement.Default) \n
		Sets or queries the offset of the track waveform. If method RsMxo.Measurement.Track.Contiunous.set is ON, use the command
		to query the current value. If method RsMxo.Measurement.Track.Contiunous.set is OFF, the command sets the offset. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: vertical_offset: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:TRACk:OFFSet?')
		return Conversions.str_to_float(response)
