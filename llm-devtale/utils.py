import tiktoken
import llm
from .node import NodeType
from typing import Dict
from .templates import (
    ROOT_LEVEL_TEMPLATE,
    SYSTEM_PROMPT,
    FOLDER_SHORT_DESCRIPTION_TEMPLATE,
    FILE_TEMPLATE,
)

prompts: Dict[NodeType, str] = {
    NodeType.FILE: FILE_TEMPLATE,
    NodeType.FOLDER: FOLDER_SHORT_DESCRIPTION_TEMPLATE,
    NodeType.REPOSITORY: ROOT_LEVEL_TEMPLATE,
}


class TokenCounter:
    @staticmethod
    def count_tokens(text: str) -> int:
        return len(tiktoken.get_encoding("cl100k_base").encode(text))


def get_prompt(summary_type: NodeType) -> str:
    prompt: str = prompts.get(summary_type, "")
    if not prompt:
        raise Exception("No template found with {summary_type}")

    return prompt


def generate_summary(llm_model: llm.Model, data: dict, summary_type: NodeType) -> str:
    prompt: str = get_prompt(summary_type).format(data=data)
    return llm_model.prompt(prompt, system=SYSTEM_PROMPT).text()


def get_llm_model(model_name: str) -> llm.Model:
    if not model_name:
        model_name = llm.get_default_model()

    return llm.get_model(model_name)
