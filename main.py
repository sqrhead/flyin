"""Entry point for the Fly-In drone routing simulation."""

import os
import sys

import arcade

from graph import Graph
from parser import ParseError, Parser
from simulation import Simulation


def main() -> None:
    """Parse the map file, run the simulation, and launch the renderer.

    The map file path can be provided as a command-line argument.
    Defaults to impossible dream if no argument is given.
    """
    filepath: str = ""
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "maps/challenger/01_the_impossible_dream.txt"

    try:
        parser: Parser = Parser(filepath)
        graph: Graph | None = parser.parse()
        if graph is None:
            print("Error: Graph is None")
            os._exit(1)

    except ParseError as pe:
        print(f"{pe}")
        os._exit(1)

    simulation: Simulation = Simulation(graph=graph)
    simulation.simulation_print_output()
    try:
        arcade.run()
    finally:
        os._exit(0)


if __name__ == "__main__":
    main()
