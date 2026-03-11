from enum import Enum
from typing import Any, Optional

# classes for the graph
# Node
class Node:
    def __init__(self, name: str, x: int, y: int, data: str) -> None:
        ...

# Edge
class Edge:
    def __init__(self, n_from: Node, n_to: Node):
        self.n_from = n_from
        self.n_to = n_to

# Graph
class Graph:
    def __init__(self) -> None:
        ...
