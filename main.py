import os
import sys
from cmath import e

import arcade

from dijkstra import Dijkstra
from drone import Drone
from graph import Graph
from parser import Parser
from renderer import Renderer
from simulation import Simulation


def main() -> None:
    # maps/challenger/01_the_impossible_dream.txt
    parser: Parser = Parser("maps/challenger/01_the_impossible_dream.txt")
    graph: Graph = parser.parse()
    if not graph:
        raise SystemExit("Graph not found")
    simulation: Simulation = Simulation(graph=graph)
    try:
        arcade.run()
    finally:
        os._exit(0)


if __name__ == "__main__":
    main()
    # sys.exit(0)
