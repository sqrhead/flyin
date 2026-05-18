from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class Zone:
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
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1


@dataclass
class Graph:
    nb_drones: int
    zones: list[Zone] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)

    def log_graph(self) -> None:
        print(f"Number of Drones: {self.nb_drones}")
        for zone in self.zones:
            print(f"Zone: {zone.name} {zone.x} {zone.y}")
        for connection in self.connections:
            print(f"Connection: {connection.zone_a} to {connection.zone_b}")

    def get_start(self) -> Zone:
        for zone in self.zones:
            if zone.is_start:
                return zone
        raise ValueError("Zone: start not found")

    def get_end(self) -> Zone:
        for zone in self.zones:
            if zone.is_end:
                return zone
        raise ValueError("Zone: end not found")

    def get_zone_by_name(self, name: str) -> Optional[Zone]:
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None

    def get_current_connections(self, curr_zone: Zone) -> list[Connection]:
        conns: list[Connection] = []
        for conn in self.connections:
            if curr_zone.name == conn.zone_a:
                conns.append(conn)
            elif curr_zone.name == conn.zone_b:
                # Return a normalized copy with zone_a = current zone
                conns.append(Connection(conn.zone_b, conn.zone_a,
                                        conn.max_link_capacity))
        return conns
