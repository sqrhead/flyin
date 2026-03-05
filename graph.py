from enum import Enum
from typing import Any, Optional
from graph import *

class NodeType(Enum):
    START = 0
    END = 1
    HUB = 2
    CONNECTION = 3

class GraphNode:
    def __init__(self, type: NodeType, name: str, position: tuple[int, int], metadata: Optional[list[Any]] = None) -> None:
        self.type = type
        self.name = name
        self.position: tuple[int, int] = position
        self.metadata: Optional[list[Any]] = metadata

class Graph:
    ...