from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NextCls:
	"""Next commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("next", core, parent)

	def set(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: HCOPy:IMMediate:NEXT \n
		Snippet: driver.hardCopy.immediate.next.set() \n
		Starts the output of the next display image, depending on the HCOPy:DESTination<m> destination setting. If the screenshot
		is saved to a file, the file name used in the last saving process is automatically counted up to the next unused name. To
		define the file name, use method RsMxo.MassMemory.name. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'HCOPy:IMMediate:NEXT', opc_timeout_ms)
		# OpcSyncAllowed = true
