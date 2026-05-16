from dataclasses import dataclass
from typing import Union

from dijkstra import Dijkstra
from drone import Drone
from graph import Connection, Graph, Zone, ZoneType
from renderer import Renderer
from vars import ARC_COLORS


class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.start = graph.get_start()
        self.end = graph.get_end()
        self.table: dict[tuple[str, int], int] = {}
        dijkstra: Dijkstra = Dijkstra()

        self.drone_color_pool = [
            v
            for k, v in ARC_COLORS.items()
            if k not in ["green", "red", "orange", "black", "rainbow"]
        ]
        self.drones: list[Drone] = []
        for n in range(graph.nb_drones):
            chosen_color = self.drone_color_pool[n % len(self.drone_color_pool)]
            self.drones.append(Drone(n, color=chosen_color))

        for drone in self.drones:
            schedule = dijkstra.path(graph, self.table)
            # drone.path = [
            #     (item, turn) for item, turn in schedule if not isinstance(item, str)
            # ]
            drone.path = schedule
            self.update_table(schedule=schedule)
        # Print first drone path
        for drone in self.drones:
            print(f"Drone {drone.id}")
            for item, turn in drone.path:
                name = item.name if hasattr(item, "name") else item
                print(f"turn={turn} -> {name}")

        renderer: Renderer = Renderer(graph=graph, drones=self.drones)

    def update_table(self, schedule: list[tuple[any, int]]) -> None:
        for res, turn in schedule:
            name = res.name if hasattr(res, "name") else str(res)
            self.table[(name, turn)] = self.table.get((name, turn), 0) + 1
