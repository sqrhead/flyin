from typing import Any, Optional


class Drone:
    """Represents a single drone in the simulation."""
    def __init__(self, id: int, color: Optional[Any] = None) -> None:
        """Initialize a new Drone.

        Args:
            id: The integer identifier for
                the drone (converted to 'D1', 'D2', etc.).
            color: The Arcade color constant used for rendering this drone.
        """
        self.id: str = "D" + str(id + 1)
        self.path: list[tuple[Any, int]] = []
        self.color: Optional[Any] = color
