import sys

import arcade

from dijkstra import Dijkstra
from drone import Drone
from graph import Graph
from parser import Parser
from renderer import Renderer
from simulation import Simulation


def main() -> None:
    # maps/challenger/01_the_impossible_dream.txt
    parser: Parser = Parser("maps/easy/01_linear_path.txt")
    graph: Graph = parser.parse()
    if not graph:
        raise SystemExit("Graph not found")
    simulation: Simulation = Simulation(graph=graph)
    arcade.run()


if __name__ == "__main__":
    main()
    # sys.exit(0)
