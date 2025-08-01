from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get(self, layout=repcap.Layout.Default, node=repcap.Node.Default) -> int:
		"""SCPI: LAYout<*>:NODE<*>:COUNt \n
		Snippet: value: int = driver.layout.node.count.get(layout = repcap.Layout.Default, node = repcap.Node.Default) \n
		Returns the maximum number of nodes that can be defined. This number is the maximum value for the node suffix. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param node: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Node')
			:return: count: Maximum value for the node suffix"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		node_cmd_val = self._cmd_group.get_repcap_cmd_value(node, repcap.Node)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:NODE{node_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
