from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """Enumeration of available zone behaviors and movement costs."""
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class Zone:
    """Represents a single node/hub in the map network."""
    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            zone_type: ZoneType = ZoneType.NORMAL,
            color: Optional[str] = None,
            max_drones: int = 1,
            is_start: bool = False,
            is_end: bool = False) -> None:
        """Initialize a Zone with coordinates, capacity, and metadata.

        Args:
            name: The unique string identifier for the zone.
            x: X-coordinate for rendering.
            y: Y-coordinate for rendering.
            zone_type: The ZoneType enum dictating movement rules.
            color: Optional string representing the zone's color.
            max_drones: Maximum number of drones allowed simultaneously.
            is_start: Boolean flag indicating if this is the start hub.
            is_end: Boolean flag indicating if this is the goal hub.
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: ZoneType = zone_type
        self.color: Optional[str] = color
        self.max_drones: int = max_drones
        self.is_start: bool = is_start
        self.is_end: bool = is_end


@dataclass
class Connection:
    """Represents a bidirectional link between two zones."""
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1


@dataclass
class Graph:
    """Stores the complete network topology of zones and connections."""
    nb_drones: int
    zones: list[Zone] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)

    def get_start(self) -> Zone:
        """Locate and return the start zone.

        Returns:
            The Zone object marked as is_start.

        Raises:
            ValueError: If no start zone exists in the graph.
        """
        for zone in self.zones:
            if zone.is_start:
                return zone
        raise ValueError("Zone: start not found")

    def get_end(self) -> Zone:
        """Locate and return the end zone.

        Returns:
            The Zone object marked as is_end.

        Raises:
            ValueError: If no end zone exists in the graph.
        """
        for zone in self.zones:
            if zone.is_end:
                return zone
        raise ValueError("Zone: end not found")

    def get_zone_by_name(self, name: str) -> Optional[Zone]:
        """Find a zone by its unique name.

        Args:
            name: The string name of the target zone.

        Returns:
            The matching Zone object, or None if not found.
        """
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None

    def get_current_connections(self, curr_zone: Zone) -> list[Connection]:
        """Retrieve all connections attached to a specific zone.

        Normalizes the returned connections so that 'zone_a' is always
        the provided curr_zone, making traversal logic simpler.

        Args:
            curr_zone: The Zone object to find connections for.

        Returns:
            A list of Connection objects attached to the current zone.
        """
        conns: list[Connection] = []
        for conn in self.connections:
            if curr_zone.name == conn.zone_a:
                conns.append(conn)
            elif curr_zone.name == conn.zone_b:
                # Return a normalized copy with zone_a = current zone
                conns.append(Connection(conn.zone_b, conn.zone_a,
                                        conn.max_link_capacity))
        return conns
