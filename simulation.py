from typing import Union

from graph import Graph, Zone, Connection, ZoneType
from dataclasses import dataclass


class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.total_turns: int = 1
        self.start = graph.get_start()
        self.end = graph.get_end()
        self.table: dict[tuple[str, int], int] = {} 

    def update_table(self, schedule: list[tuple[any, int]]) -> None:
        for res, turn in schedule:
            name = res.name if hasattr(res, 'name') else str(res)
            if name == self.start.name:
                continue
            self.table[(name, turn)] = self.table.get((name, turn), 0) + 1


    def execute_turn(self) -> None:
        ...