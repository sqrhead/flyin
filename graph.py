from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


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
