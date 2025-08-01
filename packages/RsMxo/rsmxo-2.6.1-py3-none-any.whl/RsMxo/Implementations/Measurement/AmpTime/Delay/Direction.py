from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DirectionCls:
	"""Direction commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("direction", core, parent)

	def set(self, edge_cnt_dirct: enums.EdgeCntDirct, measurement=repcap.Measurement.Default, delay=repcap.Delay.Default) -> None:
		"""SCPI: MEASurement<*>:AMPTime:DELay<*>:DIRection \n
		Snippet: driver.measurement.ampTime.delay.direction.set(edge_cnt_dirct = enums.EdgeCntDirct.FRFI, measurement = repcap.Measurement.Default, delay = repcap.Delay.Default) \n
		Selects the direction for counting slopes for each source: from the beginning of the waveform, or from the end. \n
			:param edge_cnt_dirct: FRFI - FRom FIrst, counting starts with the first edge of the waveform. FRLA - FRom LAst, counting starts with the last edge of the waveform.
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param delay: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Delay')
		"""
		param = Conversions.enum_scalar_to_str(edge_cnt_dirct, enums.EdgeCntDirct)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		delay_cmd_val = self._cmd_group.get_repcap_cmd_value(delay, repcap.Delay)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:AMPTime:DELay{delay_cmd_val}:DIRection {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default, delay=repcap.Delay.Default) -> enums.EdgeCntDirct:
		"""SCPI: MEASurement<*>:AMPTime:DELay<*>:DIRection \n
		Snippet: value: enums.EdgeCntDirct = driver.measurement.ampTime.delay.direction.get(measurement = repcap.Measurement.Default, delay = repcap.Delay.Default) \n
		Selects the direction for counting slopes for each source: from the beginning of the waveform, or from the end. \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param delay: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Delay')
			:return: edge_cnt_dirct: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		delay_cmd_val = self._cmd_group.get_repcap_cmd_value(delay, repcap.Delay)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:AMPTime:DELay{delay_cmd_val}:DIRection?')
		return Conversions.str_to_scalar_enum(response, enums.EdgeCntDirct)
