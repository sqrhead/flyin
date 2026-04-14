from dataclasses import dataclass, field
from enum import Enum
from drone import Drone

class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class Zone:
    def __init__(self, name, x, y, zone_type=ZoneType.NORMAL, color=None, max_drones=1, is_start=False, is_end=False):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type: ZoneType = zone_type
        self.color = color
        self.max_drones = max_drones
        self.is_start = is_start
        self.is_end = is_end

@dataclass
class Connection:
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1


@dataclass
class Graph:
    nb_drones: int
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)

    def log_graph(self) -> None:
        print(f"Number of Drones: {self.nb_drones}")
        for zone in self.zones:
            print(f"Zone: {zone.name} {zone.x} {zone.y}")
        for connection in self.connections:
            print(f"Connection: {connection}")

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

    def get_zone_by_name(self, name: str) -> Zone:
        for zone in self.zones:
            if zone.name == name:
                return zone

    def get_current_connections(self, curr_zone: Zone) -> list[Connection]:
        conns = []
        for conn in self.connections:
            if curr_zone.name == conn.zone_a:
                conns.append(conn)
        return conns