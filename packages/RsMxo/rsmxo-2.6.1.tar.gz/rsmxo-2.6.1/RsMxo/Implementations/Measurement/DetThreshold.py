from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DetThresholdCls:
	"""DetThreshold commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("detThreshold", core, parent)

	def set(self, sign_detect_thres: float, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:DETThreshold \n
		Snippet: driver.measurement.detThreshold.set(sign_detect_thres = 1.0, measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param sign_detect_thres: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(sign_detect_thres)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:DETThreshold {param}')

	def get(self, measurement=repcap.Measurement.Default) -> float:
		"""SCPI: MEASurement<*>:DETThreshold \n
		Snippet: value: float = driver.measurement.detThreshold.get(measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: sign_detect_thres: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:DETThreshold?')
		return Conversions.str_to_float(response)
