from enum import Enum
from typing import Any, Optional

# classes for the graph
# Node
class Node:
    def __init__(self, name: str, x: int, y: int, data: str) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.data = data
        ...

# Edge
class Edge:
    def __init__(self, n_from: Node, n_to: Node):
        self.n_from = n_from
        self.n_to = n_to

# Graph
class Graph:
    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def show(self) -> None:
        for n in self.nodes:
            print('Node:' , n.name)

        for e in self.edges:
            print('Edge:', e.n_from.name, e.n_to.name)

if __name__ == '__main__':

    node1 = Node('node1', 0, 0, None)
    node2 = Node('node2', 0, 1, None)
    node3 = Node('node3', 0, 2, None)

    edge1 = Edge(node1, node2)
    edge2 = Edge(node2, node3)

    graph: Graph = Graph([node1, node2, node3], [edge1, edge2])
    graph.show()
