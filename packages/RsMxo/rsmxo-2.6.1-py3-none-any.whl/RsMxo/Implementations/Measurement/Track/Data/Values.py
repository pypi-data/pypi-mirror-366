from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValuesCls:
	"""Values commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("values", core, parent)

	def get(self, measurement=repcap.Measurement.Default) -> bytes:
		"""SCPI: MEASurement<*>:TRACk:DATA[:VALues] \n
		Snippet: value: bytes = driver.measurement.track.data.values.get(measurement = repcap.Measurement.Default) \n
		Returns the data of the indicated track waveform for transmission from the instrument to the controlling computer.
		The data can be used in MATLAB, for example. Without parameters, the complete waveform is retrieved. Using the offset and
		length parameters, data can be retrieved in smaller portions, which makes the command faster. If you send only one
		parameter, it is interpreted as offset, and the data is retrieved from offset to the end of the waveform. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: data: List of values according to the format and content settings."""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_bin_block_ERROR(f'MEASurement{measurement_cmd_val}:TRACk:DATA:VALues?')
		return response
