import sys
import arcade

from parser import Parser
from dijkstra import Dijkstra
from drone import Drone
from simulation import Simulation
from graph import Graph
from renderer import Renderer


def main() -> None:
    # maps/challenger/01_the_impossible_dream.txt
    parser: Parser = Parser("linear_path.txt")
    graph: Graph = parser.parse()
    renderer: Renderer = Renderer()
    if not graph:
        raise SystemExit("Graph not found")
    dijkstra: Dijkstra = Dijkstra()
    simulation: Simulation = Simulation(graph=graph)

    drones: list[Drone] = [Drone(n) for n in range(graph.nb_drones)]

    for drone in drones:
        schedule = dijkstra.path(graph, simulation.table)
        drone.path = [item for item, turn in schedule if not isinstance(item, str)]
        simulation.update_table(schedule=schedule)

    for el in simulation.table:
        print(el)

    renderer.setup()
    arcade.run()

if __name__ == '__main__':
    main()
    sys.exit(0)