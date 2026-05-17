
from dijkstra import Dijkstra
from drone import Drone
from graph import Graph
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
            chosen_color = self.drone_color_pool[
                n % len(self.drone_color_pool)
                ]
            self.drones.append(Drone(n, color=chosen_color))

        for drone in self.drones:
            schedule = dijkstra.path(graph, self.table)

            drone.path = schedule
            self.update_table(schedule=schedule)

        renderer: Renderer = Renderer(graph=graph, drones=self.drones)

    def update_table(self, schedule: list[tuple[any, int]]) -> None:
        for res, turn in schedule:
            name = res.name if hasattr(res, "name") else str(res)
            self.table[(name, turn)] = self.table.get((name, turn), 0) + 1

    def simulation_print_output(self) -> None:
        max_turns = max(
            turn
            for drone in self.drones
            for _, turn in drone.path
            )

        for turn in range(max_turns + 1):
            turn_actions = []
            for drone in self.drones:
                step = next(
                    (item
                     for item, t in drone.path
                     if t == turn
                     ), None)
                if step:
                    if hasattr(step, "name"):
                        turn_actions.append(f"{drone.id}({step.name})")
                    else:
                        turn_actions.append(f"{drone.id}-{step}")

            print(f"T{turn:02} " + " ".join(turn_actions))
