from enum import Enum

class Drone:
    def __init__(self, id: int):
        self.id: str = "ID_" + str(id)
        self.path: list = []