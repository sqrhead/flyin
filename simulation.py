# Simulation file

class Drone:
    def __init__(self, id: int): 
        self.id = "ID_" + str(id)

class Simulation:
    def __init__(self) -> None:
        self.total_turns: int = 1

    def execute_turn(self) -> None:
        ...