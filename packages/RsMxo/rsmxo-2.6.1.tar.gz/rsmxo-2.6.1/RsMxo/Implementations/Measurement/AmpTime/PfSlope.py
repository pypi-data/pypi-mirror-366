from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PfSlopeCls:
	"""PfSlope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pfSlope", core, parent)

	def set(self, period_slope: enums.PeriodSlope, measurement=repcap.Measurement.Default) -> None:
		"""SCPI: MEASurement<*>:AMPTime:PFSLope \n
		Snippet: driver.measurement.ampTime.pfSlope.set(period_slope = enums.PeriodSlope.EITHer, measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param period_slope: No help available
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(period_slope, enums.PeriodSlope)
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		self._core.io.write(f'MEASurement{measurement_cmd_val}:AMPTime:PFSLope {param}')

	# noinspection PyTypeChecker
	def get(self, measurement=repcap.Measurement.Default) -> enums.PeriodSlope:
		"""SCPI: MEASurement<*>:AMPTime:PFSLope \n
		Snippet: value: enums.PeriodSlope = driver.measurement.ampTime.pfSlope.get(measurement = repcap.Measurement.Default) \n
		No command help available \n
			:param measurement: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Measurement')
			:return: period_slope: No help available"""
		measurement_cmd_val = self._cmd_group.get_repcap_cmd_value(measurement, repcap.Measurement)
		response = self._core.io.query_str(f'MEASurement{measurement_cmd_val}:AMPTime:PFSLope?')
		return Conversions.str_to_scalar_enum(response, enums.PeriodSlope)
