from ..graph.node import Node
from ..graph.port import PortType, InputPort


class ButtonTrigger(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="ButtonTrigger",
            category="triggers",
            task_name="triggers.button_trigger",
            node_id=id,
            ports={
                "button_text": InputPort(
                    name="button_text",
                    port_type=PortType.INPUT,
                    value="",
                ),
            },
        )
