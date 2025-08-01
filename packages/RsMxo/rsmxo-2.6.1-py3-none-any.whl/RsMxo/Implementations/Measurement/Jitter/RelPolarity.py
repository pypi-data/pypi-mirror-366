from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RelPolarityCls:
	"""RelPolarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("relPolarity", core, parent)

	def set(self, relative_polarity: enums.RelativePolarity, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:JITTer:RELPolarity \n
		Snippet: driver.measurement.jitter.relPolarity.set(relative_polarity = enums.RelativePolarity.INVerse, measurement = repcap.Measurement.Default) \n
		Sets the edge of the second waveform relative to the first waveform. \n
			:param relative_polarity:
				- MATChing: Measures from positive to positive edge or from negative to negative edge.
				- INVerse: Measures from positive to negative edge or from negative to positive edge.
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')"""
		param = Conversions.enum_scalar_to_str(relative_polarity, enums.RelativePolarity)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:JITTer:RELPolarity {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default) -> enums.RelativePolarity:
		"""SCPI: MEASurement<*>:JITTer:RELPolarity \n
		Snippet: value: enums.RelativePolarity = driver.measurement.jitter.relPolarity.get(measurement = repcap.Measurement.Default) \n
		Sets the edge of the second waveform relative to the first waveform. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: relative_polarity: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:JITTer:RELPolarity?')
		return Conversions.str_to_scalar_enum(response, enums.RelativePolarity)
