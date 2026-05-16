from enum import Enum


class Drone:
    def __init__(self, id: int, color=None) -> None:
        self.id: str = "ID_" + str(id)
        self.path: list = []
        self.color = color
