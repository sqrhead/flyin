from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from drone import Drone 

class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False
    line_nb: int = 0 # used to print ln for validation
    drone: list[Drone] = [] # to keep info on drones


# should i put a drone list here too for the waiting drones 
@dataclass
class Connection:
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    def involves(self, name: str) -> bool:
        return name in [self.zone_a, self.zone_b]


@dataclass
class Graph:
    nb_drones: int
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)

    def log_graph(self) -> None:
        print(f"Number of Drones: {self.nb_drones}")
        for zone in self.zones:
            print(f"Zone: {zone}")
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