from typing import Any, Optional


class Drone:
    def __init__(self, id: int, color: Optional[Any] = None) -> None:
        self.id: str = "D" + str(id + 1)
        self.path: list[tuple[Any, int]] = []
        self.color: Optional[Any] = color
