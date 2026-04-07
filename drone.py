from enum import Enum

class DroneStatus(Enum):
    WAIT = 0
    MOVE = 1
    REACHED = 2

class Drone:
    def __init__(self, id: int):
        self.id: str = "ID_" + str(id)
        self.status: DroneStatus = DroneStatus.WAIT
        self.path: list = []