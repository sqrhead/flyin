import os
import arcade

from graph import Graph
from parser import Parser
from simulation import Simulation


def main() -> None:
    # maps/challenger/01_the_impossible_dream.txt
    parser: Parser = Parser("maps/easy/01_linear_path.txt")
    graph: Graph = parser.parse()
    if not graph:
        raise SystemExit("Graph not found")
    simulation: Simulation = Simulation(graph=graph)
    simulation.simulation_print_output()
    try:
        arcade.run()
    finally:
        os._exit(0)


if __name__ == "__main__":
    main()
    # sys.exit(0)
