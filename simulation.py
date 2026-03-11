# Simulation file


class Simulation:
    def __init__(self) -> None:
        self.total_turns: int = 1

    def execute_turn(self) -> None:
        ...