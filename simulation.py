"""Simulation module orchestrating drone pathfinding and output."""

import os
from typing import Any

from dijkstra import Dijkstra
from drone import Drone
from graph import Graph, Zone
from renderer import Renderer
from vars import DRN_COLORS


class Simulation:
    """Runs the full drone routing simulation.

    Computes a path for each drone sequentially using a shared occupancy table,
    then drives the renderer and prints the formatted simulation output.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize and run the simulation.

        Computes paths for all drones and sets up the renderer.

        Args:
            graph: The parsed zone graph to simulate on.
        """
        self.graph: Graph = graph
        self.end: Zone = graph.get_end()
        self.table: dict[tuple[str, int], int] = {}
        dijkstra: Dijkstra = Dijkstra()

        self.drones: list[Drone] = []
        for n in range(graph.nb_drones):
            chosen_color = DRN_COLORS[
                n % len(DRN_COLORS)
            ]
            self.drones.append(Drone(n, color=chosen_color))

        for drone in self.drones:
            schedule = dijkstra.path(graph, self.table)
            if not schedule:
                print(f"Error:infinite loop detected {drone.id} drone")
                os._exit(1)
            drone.path = schedule
            for step, turn in drone.path:
                if hasattr(step, "name"):
                    self.table[(step.name, turn)] = self.table.get(
                        (step.name, turn), 0) + 1
                else:
                    self.table[(step, turn)] = self.table.get(
                        (step, turn), 0) + 1

            for i in range(len(drone.path) - 1):
                curr_step, curr_turn = drone.path[i]
                next_step, next_turn = drone.path[i + 1]

                if hasattr(curr_step, "name") and hasattr(next_step, "name"):
                    if curr_step.name != next_step.name:
                        link_k = (
                            f"{min(curr_step.name, next_step.name)}-"
                            f"{max(curr_step.name, next_step.name)}"
                        )
                        link_tran_turn = curr_turn + 1

                        self.table[(link_k, link_tran_turn)] = self.table.get(
                            (link_k, link_tran_turn), 0) + 1
        self.renderer: Renderer = Renderer(graph=graph, drones=self.drones)

    def simulation_print_output(self) -> None:
        """Print the simulation output in the required format.

        Each line represents one turn and lists only the drones that moved
        (i.e. changed zone or entered a link), using the format:
        D<ID>-<zone_or_link>

        Drones that are waiting (staying in the same zone) are omitted.
        Drones that have reached the end zone are no longer tracked.
        The simulation ends when all drones have been delivered.
        """
        if not any(drone.path for drone in self.drones):
            return

        end_name: str = self.end.name

        max_turns: int = max(
            turn
            for drone in self.drones
            for _, turn in drone.path
        )

        delivered: set[str] = set()
        with open("output.txt", "w") as f:
            for turn in range(max_turns + 1):
                turn_actions: list[str] = []

                for drone in self.drones:
                    if drone.id in delivered:
                        continue

                    step: Any = next(
                        (item for item, t in drone.path if t == turn),
                        None
                    )
                    if step is None:
                        continue

                    prev_step: Any = next(
                        (item for item, t in drone.path if t == turn - 1),
                        None
                    )

                    if prev_step is None:
                        continue

                    if isinstance(step, str):
                        turn_actions.append(f"{drone.id}-{step}")
                        continue

                    if hasattr(step, "name"):
                        if (hasattr(prev_step, "name")
                                and prev_step.name == step.name):
                            continue

                        turn_actions.append(f"{drone.id}-{step.name}")
                        if step.name == end_name:
                            delivered.add(drone.id)

                if turn_actions:
                    line_out = " ".join(turn_actions)
                    print(line_out)
                    f.write(line_out + "\n")
