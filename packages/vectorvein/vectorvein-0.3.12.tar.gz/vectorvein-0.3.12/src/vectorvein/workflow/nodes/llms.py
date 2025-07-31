from ..graph.node import Node
from ..graph.port import PortType, InputPort, OutputPort


class AliyunQwen(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="AliyunQwen",
            category="llms",
            task_name="llms.aliyun_qwen",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXT,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="qwen3-32b",
                    options=[
                        {"value": "qwen2.5-72b-instruct", "label": "qwen2.5-72b-instruct"},
                        {"value": "qwen2.5-32b-instruct", "label": "qwen2.5-32b-instruct"},
                        {"value": "qwen2.5-coder-32b-instruct", "label": "qwen2.5-coder-32b-instruct"},
                        {"value": "qwq-32b", "label": "qwq-32b"},
                        {"value": "qwen2.5-14b-instruct", "label": "qwen2.5-14b-instruct"},
                        {"value": "qwen2.5-7b-instruct", "label": "qwen2.5-7b-instruct"},
                        {"value": "qwen2.5-coder-7b-instruct", "label": "qwen2.5-coder-7b-instruct"},
                        {"value": "qwen3-235b-a22b", "label": "qwen3-235b-a22b"},
                        {"value": "qwen3-235b-a22b-thinking", "label": "qwen3-235b-a22b-thinking"},
                        {"value": "qwen3-32b", "label": "qwen3-32b"},
                        {"value": "qwen3-32b-thinking", "label": "qwen3-32b-thinking"},
                        {"value": "qwen3-30b-a3b", "label": "qwen3-30b-a3b"},
                        {"value": "qwen3-30b-a3b-thinking", "label": "qwen3-30b-a3b-thinking"},
                        {"value": "qwen3-14b", "label": "qwen3-14b"},
                        {"value": "qwen3-14b-thinking", "label": "qwen3-14b-thinking"},
                        {"value": "qwen3-8b", "label": "qwen3-8b"},
                        {"value": "qwen3-8b-thinking", "label": "qwen3-8b-thinking"},
                        {"value": "qwen3-4b", "label": "qwen3-4b"},
                        {"value": "qwen3-4b-thinking", "label": "qwen3-4b-thinking"},
                        {"value": "qwen3-1.7b", "label": "qwen3-1.7b"},
                        {"value": "qwen3-1.7b-thinking", "label": "qwen3-1.7b-thinking"},
                        {"value": "qwen3-0.6b", "label": "qwen3-0.6b"},
                        {"value": "qwen3-0.6b-thinking", "label": "qwen3-0.6b-thinking"},
                    ],
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class Baichuan(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Baichuan",
            category="llms",
            task_name="llms.baichuan",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="Baichuan3-Turbo",
                    options=[
                        {"value": "Baichuan4", "label": "Baichuan4"},
                        {"value": "Baichuan3-Turbo", "label": "Baichuan3-Turbo"},
                        {"value": "Baichuan3-Turbo-128k", "label": "Baichuan3-Turbo-128k"},
                        {"value": "Baichuan2-Turbo", "label": "Baichuan2-Turbo"},
                        {"value": "Baichuan2-53B", "label": "Baichuan2-53B"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class BaiduWenxin(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="BaiduWenxin",
            category="llms",
            task_name="llms.baidu_wenxin",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="ernie-3.5",
                    options=[
                        {"value": "ernie-lite", "label": "ernie-lite"},
                        {"value": "ernie-speed", "label": "ernie-speed"},
                        {"value": "ernie-3.5", "label": "ernie-3.5"},
                        {"value": "ernie-4.0", "label": "ernie-4.0"},
                        {"value": "ernie-4.5", "label": "ernie-4.5"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "output": OutputPort(),
            },
        )


class ChatGLM(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="ChatGLM",
            category="llms",
            task_name="llms.chat_glm",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="glm-4-air",
                    options=[
                        {"value": "glm-4-plus", "label": "glm-4-plus"},
                        {"value": "glm-4", "label": "glm-4"},
                        {"value": "glm-4-0520", "label": "glm-4-0520"},
                        {"value": "glm-4-air", "label": "glm-4-air"},
                        {"value": "glm-4-airx", "label": "glm-4-airx"},
                        {"value": "glm-4-flash", "label": "glm-4-flash"},
                        {"value": "glm-4-long", "label": "glm-4-long"},
                        {"value": "glm-zero-preview", "label": "glm-zero-preview"},
                        {"value": "glm-z1-air", "label": "glm-z1-air"},
                        {"value": "glm-z1-airx", "label": "glm-z1-airx"},
                        {"value": "glm-z1-flash", "label": "glm-z1-flash"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class Claude(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Claude",
            category="llms",
            task_name="llms.claude",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="claude-sonnet-4-20250514",
                    options=[
                        {"value": "claude-opus-4-20250514-thinking", "label": "claude-opus-4-20250514-thinking"},
                        {"value": "claude-opus-4-20250514", "label": "claude-opus-4-20250514"},
                        {"value": "claude-sonnet-4-20250514-thinking", "label": "claude-sonnet-4-20250514-thinking"},
                        {"value": "claude-sonnet-4-20250514", "label": "claude-sonnet-4-20250514"},
                        {"value": "claude-3-7-sonnet-thinking", "label": "claude-3-7-sonnet-thinking"},
                        {"value": "claude-3-7-sonnet", "label": "claude-3-7-sonnet"},
                        {"value": "claude-3-5-sonnet", "label": "claude-3-5-sonnet"},
                        {"value": "claude-3-5-haiku", "label": "claude-3-5-haiku"},
                        {"value": "claude-3-opus", "label": "claude-3-opus"},
                        {"value": "claude-3-sonnet", "label": "claude-3-sonnet"},
                        {"value": "claude-3-haiku", "label": "claude-3-haiku"},
                    ],
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "output": OutputPort(),
            },
        )


class Deepseek(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Deepseek",
            category="llms",
            task_name="llms.deepseek",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="deepseek-chat",
                    options=[
                        {"value": "deepseek-chat", "label": "deepseek-chat"},
                        {"value": "deepseek-reasoner", "label": "deepseek-r1"},
                        {"value": "deepseek-r1-distill-qwen-32b", "label": "deepseek-r1-distill-qwen-32b"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "reasoning_content": OutputPort(
                    name="reasoning_content",
                    condition="return fieldsData.llm_model.value === 'deepseek-reasoner'",
                    condition_python=lambda ports: ports["llm_model"].value == "deepseek-reasoner",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class Gemini(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Gemini",
            category="llms",
            task_name="llms.gemini",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="gemini-2.5-pro-preview-06-05",
                    options=[
                        {"label": "gemini-2.0-flash", "value": "gemini-2.0-flash"},
                        {"label": "gemini-2.0-flash-lite-preview-02-05", "value": "gemini-2.0-flash-lite-preview-02-05"},
                        {"value": "gemini-2.0-flash-thinking-exp-01-21", "label": "gemini-2.0-flash-thinking-exp-01-21"},
                        {"label": "gemini-2.5-pro-preview-06-05", "value": "gemini-2.5-pro-preview-06-05"},
                        {"label": "gemini-2.5-flash-preview-05-20", "value": "gemini-2.5-flash-preview-05-20"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class LingYiWanWu(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="LingYiWanWu",
            category="llms",
            task_name="llms.ling_yi_wan_wu",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="yi-lightning",
                    options=[
                        {
                            "value": "yi-lightning",
                            "label": "yi-lightning",
                        },
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "output": OutputPort(),
            },
        )


class MiniMax(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="MiniMax",
            category="llms",
            task_name="llms.mini_max",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="MiniMax-Text-01",
                    options=[
                        {"value": "abab6.5s-chat", "label": "abab6.5s-chat"},
                        {"value": "MiniMax-Text-01", "label": "MiniMax-Text-01"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class Moonshot(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Moonshot",
            category="llms",
            task_name="llms.moonshot",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="moonshot-v1-8k",
                    options=[
                        {"value": "moonshot-v1-8k", "label": "moonshot-v1-8k"},
                        {"value": "moonshot-v1-32k", "label": "moonshot-v1-32k"},
                        {"value": "moonshot-v1-128k", "label": "moonshot-v1-128k"},
                        {"value": "kimi-latest", "label": "kimi-latest"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class OpenAI(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="OpenAI",
            category="llms",
            task_name="llms.open_ai",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="gpt-4o-mini",
                    options=[
                        {"value": "gpt-3.5", "label": "gpt-3.5-turbo"},
                        {"value": "gpt-4", "label": "gpt-4-turbo"},
                        {"value": "gpt-4o", "label": "gpt-4o"},
                        {"value": "gpt-4o-mini", "label": "gpt-4o-mini"},
                        {"value": "o1-mini", "label": "o1-mini"},
                        {"value": "o1-preview", "label": "o1-preview"},
                        {"value": "o3-mini", "label": "o3-mini"},
                        {"value": "o3-mini-high", "label": "o3-mini-high"},
                        {"value": "gpt-4.1", "label": "gpt-4.1"},
                        {"value": "o4-mini", "label": "o4-mini"},
                        {"value": "o4-mini-high", "label": "o4-mini-high"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class XAi(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="XAi",
            category="llms",
            task_name="llms.x_ai",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="grok-3-beta",
                    options=[
                        {"value": "grok-beta", "label": "grok-beta"},
                        {"value": "grok-3-beta", "label": "grok-3-beta"},
                        {"value": "grok-3-fast-beta", "label": "grok-3-fast-beta"},
                        {"value": "grok-3-mini-beta", "label": "grok-3-mini-beta"},
                        {"value": "grok-3-mini-fast-beta", "label": "grok-3-mini-fast-beta"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class CustomModel(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="CustomModel",
            category="llms",
            task_name="llms.custom_model",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "model_family": InputPort(
                    name="model_family",
                    port_type=PortType.SELECT,
                    value="",
                    options=[],
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="",
                    options=[],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )
