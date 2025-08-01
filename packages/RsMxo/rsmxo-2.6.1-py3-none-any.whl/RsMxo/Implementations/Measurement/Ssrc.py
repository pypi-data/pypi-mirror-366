from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SsrcCls:
	"""Ssrc commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ssrc", core, parent)

	def set(self, source_2: enums.Source, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:SSRC \n
		Snippet: driver.measurement.ssrc.set(source_2 = enums.Source.C1, measurement = repcap.Measurement.Default) \n
		Defines the second measurement source. The command is an alternative to method RsMxo.Measurement.Source.set. \n
			:param source_2: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(source_2, enums.Source)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:SSRC {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default) -> enums.Source:
		"""SCPI: MEASurement<*>:SSRC \n
		Snippet: value: enums.Source = driver.measurement.ssrc.get(measurement = repcap.Measurement.Default) \n
		Defines the second measurement source. The command is an alternative to method RsMxo.Measurement.Source.set. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: source_2: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:SSRC?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
