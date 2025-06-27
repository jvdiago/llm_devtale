import tiktoken
import llm

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class TokenCounter:
    @staticmethod
    def count_tokens(text: str) -> int:
        return len(tiktoken.get_encoding("cl100k_base").encode(text))


def split_text(text: str, chunk_size: int = 1000) -> str:
    return text


class NodeType(Enum):
    FILE = "file"
    FOLDER = "folder"
    REPOSITORY = "project"


@dataclass
class Node:
    name: str
    description: str
    node_type: NodeType

    children: List["Node"] = field(default_factory=list)

    def print(self, indent: int = 0):
        spacer = " " * indent
        print(f"{spacer}{self.name}: {self.description}")
        for child in self.children:
            child.print(indent + 4)

    def add_children(self, children: "Node") -> None:
        self.children.append(children)


def generate_summary(llm_model: llm.Model, data: dict, summary_type: NodeType) -> str:
    prompt: str = ""
    ## return llm_model.prompt(prompt).text()
    return f"Summary for {data} of type {summary_type}"


def get_llm_model(model_name: str) -> llm.Model:
    return llm.get_model(model_name)
