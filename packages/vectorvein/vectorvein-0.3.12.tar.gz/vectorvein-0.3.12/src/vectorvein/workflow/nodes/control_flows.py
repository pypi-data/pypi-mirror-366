from ..graph.node import Node
from ..graph.port import PortType, InputPort, OutputPort


class Conditional(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Conditional",
            category="control_flows",
            task_name="control_flows.conditional",
            node_id=id,
            ports={
                "field_type": InputPort(
                    name="field_type",
                    port_type=PortType.SELECT,
                    value="string",
                    options=[
                        {"value": "string", "label": "Str"},
                        {"value": "number", "label": "Number"},
                    ],
                ),
                "left_field": InputPort(
                    name="left_field",
                    port_type=PortType.INPUT,
                    value="",
                ),
                "operator": InputPort(
                    name="operator",
                    port_type=PortType.SELECT,
                    value="equal",
                    options=[
                        {"value": "equal", "label": "equal", "field_type": ["string", "number"]},
                        {"value": "not_equal", "label": "not_equal", "field_type": ["string", "number"]},
                        {"value": "greater_than", "label": "greater_than", "field_type": ["number"]},
                        {"value": "less_than", "label": "less_than", "field_type": ["number"]},
                        {"value": "greater_than_or_equal", "label": "greater_than_or_equal", "field_type": ["number"]},
                        {"value": "less_than_or_equal", "label": "less_than_or_equal", "field_type": ["number"]},
                        {"value": "include", "label": "include", "field_type": ["string"]},
                        {"value": "not_include", "label": "not_include", "field_type": ["string"]},
                        {"value": "is_empty", "label": "is_empty", "field_type": ["string"]},
                        {"value": "is_not_empty", "label": "is_not_empty", "field_type": ["string"]},
                        {"value": "starts_with", "label": "starts_with", "field_type": ["string"]},
                        {"value": "ends_with", "label": "ends_with", "field_type": ["string"]},
                    ],
                ),
                "right_field": InputPort(
                    name="right_field",
                    port_type=PortType.INPUT,
                    value="",
                ),
                "true_output": InputPort(
                    name="true_output",
                    port_type=PortType.INPUT,
                    value="",
                ),
                "false_output": InputPort(
                    name="false_output",
                    port_type=PortType.INPUT,
                    value="",
                ),
                "output": OutputPort(),
            },
        )


class Empty(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Empty",
            category="control_flows",
            task_name="control_flows.empty",
            node_id=id,
            ports={
                "input": InputPort(
                    name="input",
                    port_type=PortType.INPUT,
                    value="",
                ),
                "output": OutputPort(),
            },
        )


class HumanFeedback(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="HumanFeedback",
            category="control_flows",
            task_name="control_flows.human_feedback",
            node_id=id,
            ports={
                "hint_message": InputPort(
                    name="hint_message",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "human_input": InputPort(
                    name="human_input",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "output": OutputPort(),
            },
        )


class JsonProcess(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="JsonProcess",
            category="control_flows",
            task_name="control_flows.json_process",
            node_id=id,
            ports={
                "input": InputPort(
                    name="input",
                    port_type=PortType.INPUT,
                    value="",
                ),
                "process_mode": InputPort(
                    name="process_mode",
                    port_type=PortType.SELECT,
                    value="get_value",
                    options=[
                        {"value": "get_value", "label": "get_value"},
                        {"value": "get_multiple_values", "label": "get_multiple_values"},
                        {"value": "list_values", "label": "list_values"},
                        {"value": "list_keys", "label": "list_keys"},
                    ],
                ),
                "key": InputPort(
                    name="key",
                    port_type=PortType.INPUT,
                    value="",
                    condition="return fieldsData.process_mode.value == 'get_value'",
                    condition_python=lambda ports: ports["process_mode"].value == "get_value",
                ),
                "keys": InputPort(
                    name="keys",
                    port_type=PortType.INPUT,
                    value=[],
                ),
                "default_value": InputPort(
                    name="default_value",
                    port_type=PortType.INPUT,
                    value="",
                    condition="return fieldsData.process_mode.value == 'get_value'",
                    condition_python=lambda ports: ports["process_mode"].value == "get_value",
                ),
                "output": OutputPort(),
            },
            can_add_output_ports=True,
        )


class RandomChoice(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="RandomChoice",
            category="control_flows",
            task_name="control_flows.random_choice",
            node_id=id,
            ports={
                "input": InputPort(
                    name="input",
                    port_type=PortType.LIST,
                    value=[],
                ),
                "output": OutputPort(),
            },
        )
