from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScaleCls:
	"""Scale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scale", core, parent)

	def set(self, vertical_scale: float, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:TRACk:SCALe \n
		Snippet: driver.measurement.track.scale.set(vertical_scale = 1.0, measurement = repcap.Measurement.Default) \n
		Sets or queries the vertical scale of the track diagram. If method RsMxo.Measurement.Track.Contiunous.set is ON, use the
		command to query the current value. If method RsMxo.Measurement.Track.Contiunous.set is OFF, the command sets the scale. \n
			:param vertical_scale: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(vertical_scale)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:TRACk:SCALe {param}')

	def get(self, measurement=repcap.Measurement.Default) -> float:
		"""SCPI: MEASurement<*>:TRACk:SCALe \n
		Snippet: value: float = driver.measurement.track.scale.get(measurement = repcap.Measurement.Default) \n
		Sets or queries the vertical scale of the track diagram. If method RsMxo.Measurement.Track.Contiunous.set is ON, use the
		command to query the current value. If method RsMxo.Measurement.Track.Contiunous.set is OFF, the command sets the scale. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: vertical_scale: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:TRACk:SCALe?')
		return Conversions.str_to_float(response)
