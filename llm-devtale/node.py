from dataclasses import dataclass, field
from typing import List
from enum import Enum


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
