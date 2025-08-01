from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StyleCls:
	"""Style commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("style", core, parent)

	def set(self, display_style: enums.DisplayStyle, measurement=repcap.Measurement.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""SCPI: MEASurement<*>:DISPlay:REFLevel<*>:STYLe \n
		Snippet: driver.measurement.display.refLevel.style.set(display_style = enums.DisplayStyle.LINE, measurement = repcap.Measurement.Default, refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param display_style: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.enum_scalar_to_str(display_style, enums.DisplayStyle)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:DISPlay:REFLevel{refLevel_cmd_val}:STYLe {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default, refLevel=repcap.RefLevel.Default) -> enums.DisplayStyle:
		"""SCPI: MEASurement<*>:DISPlay:REFLevel<*>:STYLe \n
		Snippet: value: enums.DisplayStyle = driver.measurement.display.refLevel.style.get(measurement = repcap.Measurement.Default, refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: display_style: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:DISPlay:REFLevel{refLevel_cmd_val}:STYLe?')
		return Conversions.str_to_scalar_enum(response, enums.DisplayStyle)
