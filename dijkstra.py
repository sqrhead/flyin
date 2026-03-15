# Dijkstra Algorithm
from typing import Optional

class Node:
    def __init__(
        self,
        n_from: str,
        n_to: str,
        weight: Optional[int] = None
    ) -> None:
        self.n_from = n_from
        self.n_to = n_to
        self.weight = weight
        ...

    def info(self) -> str:
        return f'from: {self.n_from} to: {self.n_to} weight: {self.weight}'


class Dijkstra:
    def __init__(self, graph: list[tuple[str, str, int]]) -> None:

        self.nodes = []
        for n in graph:
            self.nodes.append(Node(n[0], n[1], n[2]))

        self.graph = graph

        for n in self.nodes:
            print(n.info())

        self.visited_nodes: list[Node] = []

    def path(self, start, end) -> list[str]:
        return []

    def find_neighbors(self, node: Node) -> list[Node]:
        return []


if __name__ == '__main__':
    edges = [
        ("A", "C", 3),
        ("A", "F", 2),
        ("C", "F", 2),
        ("C", "E", 1),
        ("C", "D", 4),
        ("F", "E", 3),
        ("F", "B", 6),
        ("F", "G", 5),
        ("E", "B", 2),
        ("D", "B", 1),
        ("B", "G", 2),
    ]
    dij = Dijkstra(edges)
