"""
Parser module for the Fly-in drone routing project.

Parses the input map file format and builds a Graph object
containing zones and connections.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ParseError(Exception):
    """Raised when the input file contains a syntax or semantic error."""

    def __init__(self, line_num: int, message: str) -> None:
        """Initialize with a line number and a human-readable cause.

        Args:
            line_num: 1-based line number where the error was found.
            message:  Description of what went wrong.
        """
        super().__init__(f"Line {line_num}: {message}")
        self.line_num = line_num


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ZoneType(Enum):
    """Possible movement-cost types for a zone."""

    NORMAL = "normal"        # 1 turn cost (default)
    BLOCKED = "blocked"      # inaccessible
    RESTRICTED = "restricted"  # 2 turns cost
    PRIORITY = "priority"    # 1 turn cost, preferred by pathfinder

    @staticmethod
    def from_str(value: str, line_num: int) -> "ZoneType":
        """Parse a string into a ZoneType, raising ParseError on bad input.

        Args:
            value:    Raw string from the file (e.g. "restricted").
            line_num: Used for error reporting.

        Returns:
            The matching ZoneType member.

        Raises:
            ParseError: If the string does not match any known type.
        """
        try:
            return ZoneType(value)
        except ValueError:
            valid = ", ".join(z.value for z in ZoneType)
            raise ParseError(
                line_num,
                f"Unknown zone type '{value}'. Valid types: {valid}"
            )


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Zone:
    """Represents a node (hub) in the drone network.

    Attributes:
        name:       Unique identifier — no dashes or spaces allowed.
        x:          X coordinate (positive integer).
        y:          Y coordinate (positive integer).
        zone_type:  Movement-cost category.
        color:      Optional display color string (e.g. "red", "blue").
        max_drones: Maximum drones that may occupy this zone simultaneously.
        is_start:   True if this is the start_hub.
        is_end:     True if this is the end_hub.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    def __repr__(self) -> str:
        """Return a compact debug representation."""
        tag = " [START]" if self.is_start else " [END]" if self.is_end else ""
        return (
            f"Zone({self.name!r} @({self.x},{self.y}) "
            f"type={self.zone_type.value} cap={self.max_drones}{tag})"
        )


@dataclass
class Connection:
    """Represents a bidirectional edge between two zones.

    Attributes:
        zone_a:           Name of the first zone.
        zone_b:           Name of the second zone.
        max_link_capacity: Max drones that may traverse this edge simultaneously.
    """

    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    def involves(self, name: str) -> bool:
        """Return True if the given zone name is an endpoint of this connection.

        Args:
            name: Zone name to check.
        """
        return name in (self.zone_a, self.zone_b)

    def other(self, name: str) -> str:
        """Return the zone on the other side of this connection.

        Args:
            name: One endpoint zone name.

        Returns:
            The other endpoint zone name.

        Raises:
            ValueError: If name is not an endpoint of this connection.
        """
        if name == self.zone_a:
            return self.zone_b
        if name == self.zone_b:
            return self.zone_a
        raise ValueError(f"Zone '{name}' is not part of connection {self}")

    def __repr__(self) -> str:
        """Return a compact debug representation."""
        return (
            f"Connection({self.zone_a!r} <-> {self.zone_b!r} "
            f"cap={self.max_link_capacity})"
        )


@dataclass
class Graph:
    """The full network: zones + connections + drone count.

    Attributes:
        nb_drones:   Total number of drones to route.
        zones:       Mapping of zone name → Zone object.
        connections: List of all Connection objects.
    """

    nb_drones: int
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience helpers (no external graph library used)
    # ------------------------------------------------------------------

    @property
    def start_zone(self) -> Zone:
        """Return the unique start zone.

        Raises:
            KeyError: If no start zone exists (should not happen after parsing).
        """
        for zone in self.zones.values():
            if zone.is_start:
                return zone
        raise KeyError("No start zone defined in graph")

    @property
    def end_zone(self) -> Zone:
        """Return the unique end zone.

        Raises:
            KeyError: If no end zone exists (should not happen after parsing).
        """
        for zone in self.zones.values():
            if zone.is_end:
                return zone
        raise KeyError("No end zone defined in graph")

    def neighbors(self, zone_name: str) -> list[tuple[Zone, Connection]]:
        """Return all zones directly reachable from zone_name.

        Args:
            zone_name: Name of the source zone.

        Returns:
            List of (neighbor_zone, connection) pairs.
        """
        result: list[tuple[Zone, Connection]] = []
        for conn in self.connections:
            if conn.involves(zone_name):
                neighbor_name = conn.other(zone_name)
                result.append((self.zones[neighbor_name], conn))
        return result

    def __repr__(self) -> str:
        """Return a summary string for debugging."""
        return (
            f"Graph(drones={self.nb_drones}, "
            f"zones={len(self.zones)}, "
            f"connections={len(self.connections)})"
        )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """Reads a drone-map file and builds a validated Graph.

    Usage::

        parser = Parser("map.txt")
        graph  = parser.parse()
    """

    def __init__(self, filepath: str) -> None:
        """Store the path to the map file.

        Args:
            filepath: Path to the input file.
        """
        self._filepath = filepath

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def parse(self) -> Graph:
        """Parse the file and return a validated Graph.

        Returns:
            A fully populated Graph instance.

        Raises:
            ParseError: On any syntax or semantic violation.
            FileNotFoundError: If the file does not exist.
        """
        with open(self._filepath, "r") as fh:
            lines = fh.readlines()

        return self._process_lines(lines)

    # ------------------------------------------------------------------
    # Line-by-line processing
    # ------------------------------------------------------------------

    def _process_lines(self, lines: list[str]) -> Graph:
        """Iterate over lines, dispatch each one, then validate the result.

        Args:
            lines: Raw lines from the file (newlines still attached).

        Returns:
            A validated Graph.

        Raises:
            ParseError: On any violation.
        """
        nb_drones: Optional[int] = None
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        seen_connections: set[frozenset[str]] = set()

        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            # --- nb_drones must come first ---
            if line.startswith("nb_drones:"):
                if nb_drones is not None:
                    raise ParseError(line_num, "Duplicate 'nb_drones' declaration")
                nb_drones = self._parse_nb_drones(line, line_num)

            elif line.startswith("start_hub:"):
                if nb_drones is None:
                    raise ParseError(
                        line_num,
                        "'nb_drones' must be the first non-comment line"
                    )
                zone = self._parse_zone(line, line_num, prefix="start_hub",
                                        is_start=True)
                self._register_zone(zone, zones, line_num)

            elif line.startswith("end_hub:"):
                if nb_drones is None:
                    raise ParseError(
                        line_num,
                        "'nb_drones' must be the first non-comment line"
                    )
                zone = self._parse_zone(line, line_num, prefix="end_hub",
                                        is_end=True)
                self._register_zone(zone, zones, line_num)

            elif line.startswith("hub:"):
                if nb_drones is None:
                    raise ParseError(
                        line_num,
                        "'nb_drones' must be the first non-comment line"
                    )
                zone = self._parse_zone(line, line_num, prefix="hub")
                self._register_zone(zone, zones, line_num)

            elif line.startswith("connection:"):
                if nb_drones is None:
                    raise ParseError(
                        line_num,
                        "'nb_drones' must be the first non-comment line"
                    )
                conn = self._parse_connection(line, line_num, zones)
                key = frozenset([conn.zone_a, conn.zone_b])
                if key in seen_connections:
                    raise ParseError(
                        line_num,
                        f"Duplicate connection between "
                        f"'{conn.zone_a}' and '{conn.zone_b}'"
                    )
                seen_connections.add(key)
                connections.append(conn)

            else:
                raise ParseError(line_num, f"Unrecognised line: {line!r}")

        # --- Post-parse semantic validation ---
        if nb_drones is None:
            raise ParseError(0, "File is empty or missing 'nb_drones'")

        self._validate_graph(zones, line_num=0)

        return Graph(nb_drones=nb_drones, zones=zones, connections=connections)

    # ------------------------------------------------------------------
    # Individual parsers
    # ------------------------------------------------------------------

    def _parse_nb_drones(self, line: str, line_num: int) -> int:
        """Parse the 'nb_drones: <n>' line.

        Args:
            line:     Stripped line text.
            line_num: For error reporting.

        Returns:
            Positive integer drone count.

        Raises:
            ParseError: If the value is missing, not an integer, or not positive.
        """
        # e.g. "nb_drones: 5"
        parts = line.split(":", 1)
        if len(parts) < 2 or not parts[1].strip():
            raise ParseError(line_num, "Missing value after 'nb_drones:'")

        raw = parts[1].strip()
        if not raw.isdigit():
            raise ParseError(
                line_num,
                f"'nb_drones' must be a positive integer, got '{raw}'"
            )
        value = int(raw)
        if value <= 0:
            raise ParseError(
                line_num,
                f"'nb_drones' must be > 0, got {value}"
            )
        return value

    def _parse_zone(
        self,
        line: str,
        line_num: int,
        prefix: str,
        is_start: bool = False,
        is_end: bool = False,
    ) -> Zone:
        """Parse a hub/start_hub/end_hub line into a Zone.

        Expected format::

            <prefix>: <name> <x> <y> [key=val ...]

        Args:
            line:     Stripped line text.
            line_num: For error reporting.
            prefix:   One of 'hub', 'start_hub', 'end_hub'.
            is_start: Tag this zone as the start.
            is_end:   Tag this zone as the end.

        Returns:
            A populated Zone instance.

        Raises:
            ParseError: On any syntax or value error.
        """
        # Strip prefix and optional metadata block
        after_prefix = line[len(prefix) + 1:].strip()  # skip "prefix:"
        main_part, metadata = self._split_metadata(after_prefix, line_num)

        tokens = main_part.split()
        if len(tokens) < 3:
            raise ParseError(
                line_num,
                f"Expected '<name> <x> <y>' after '{prefix}:', got {main_part!r}"
            )

        name, raw_x, raw_y = tokens[0], tokens[1], tokens[2]

        # Validate name: no dashes or spaces
        if "-" in name or " " in name:
            raise ParseError(
                line_num,
                f"Zone name '{name}' must not contain dashes or spaces"
            )

        x = self._parse_positive_int(raw_x, "x coordinate", line_num)
        y = self._parse_positive_int(raw_y, "y coordinate", line_num)

        # Defaults
        zone_type = ZoneType.NORMAL
        color: Optional[str] = None
        max_drones = 1

        # Parse optional metadata key=value pairs
        for token in metadata:
            if "=" not in token:
                raise ParseError(
                    line_num,
                    f"Invalid metadata token '{token}' — expected key=value"
                )
            key, _, val = token.partition("=")
            if key == "zone":
                zone_type = ZoneType.from_str(val, line_num)
            elif key == "color":
                if not val:
                    raise ParseError(line_num, "'color' value must not be empty")
                color = val
            elif key == "max_drones":
                max_drones = self._parse_positive_int(
                    val, "max_drones", line_num
                )
            else:
                raise ParseError(line_num, f"Unknown zone metadata key '{key}'")

        return Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
            is_start=is_start,
            is_end=is_end,
        )

    def _parse_connection(
        self,
        line: str,
        line_num: int,
        zones: dict[str, Zone],
    ) -> Connection:
        """Parse a 'connection: <zoneA>-<zoneB> [metadata]' line.

        Args:
            line:     Stripped line text.
            line_num: For error reporting.
            zones:    Already-parsed zones dict (for existence checks).

        Returns:
            A populated Connection instance.

        Raises:
            ParseError: On any syntax or reference error.
        """
        after_prefix = line[len("connection:"):].strip()
        main_part, metadata = self._split_metadata(after_prefix, line_num)

        # The main part must be exactly "zoneA-zoneB"
        if "-" not in main_part:
            raise ParseError(
                line_num,
                f"Connection must use 'zone1-zone2' format, got {main_part!r}"
            )

        # Split only on the FIRST dash — but zone names can't have dashes,
        # so splitting once is safe and unambiguous.
        parts = main_part.split("-", 1)
        zone_a, zone_b = parts[0].strip(), parts[1].strip()

        if not zone_a or not zone_b:
            raise ParseError(line_num, "Connection zone names must not be empty")

        # Both zones must already be defined
        for name in (zone_a, zone_b):
            if name not in zones:
                raise ParseError(
                    line_num,
                    f"Connection references undefined zone '{name}'"
                )

        # A zone cannot connect to itself
        if zone_a == zone_b:
            raise ParseError(
                line_num,
                f"Self-loop connection on zone '{zone_a}' is not allowed"
            )

        # Parse optional metadata
        max_link_capacity = 1
        for token in metadata:
            if "=" not in token:
                raise ParseError(
                    line_num,
                    f"Invalid metadata token '{token}' — expected key=value"
                )
            key, _, val = token.partition("=")
            if key == "max_link_capacity":
                max_link_capacity = self._parse_positive_int(
                    val, "max_link_capacity", line_num
                )
            else:
                raise ParseError(
                    line_num,
                    f"Unknown connection metadata key '{key}'"
                )

        return Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=max_link_capacity,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _split_metadata(
        text: str, line_num: int
    ) -> tuple[str, list[str]]:
        """Separate the main part of a line from its optional [...] block.

        Args:
            text:     Text after the line prefix (e.g. "roof1 3 4 [zone=restricted]").
            line_num: For error reporting.

        Returns:
            (main_part, list_of_key_value_tokens)

        Raises:
            ParseError: If the bracket syntax is malformed.
        """
        if "[" not in text:
            return text.strip(), []

        open_idx = text.index("[")
        close_idx = text.find("]", open_idx)

        if close_idx == -1:
            raise ParseError(line_num, "Unclosed '[' in metadata block")
        if close_idx != len(text) - 1:
            raise ParseError(
                line_num,
                "Unexpected characters after closing ']'"
            )

        main_part = text[:open_idx].strip()
        raw_meta = text[open_idx + 1: close_idx].strip()
        metadata_tokens = raw_meta.split() if raw_meta else []

        return main_part, metadata_tokens

    @staticmethod
    def _parse_positive_int(raw: str, field_name: str, line_num: int) -> int:
        """Parse a string as a positive integer.

        Args:
            raw:        The raw string to parse.
            field_name: Human-readable field name for error messages.
            line_num:   For error reporting.

        Returns:
            A positive integer value.

        Raises:
            ParseError: If the string is not a positive integer.
        """
        if not raw.lstrip("-").isdigit():
            raise ParseError(
                line_num,
                f"'{field_name}' must be an integer, got '{raw}'"
            )
        value = int(raw)
        if value <= 0:
            raise ParseError(
                line_num,
                f"'{field_name}' must be a positive integer (> 0), got {value}"
            )
        return value

    @staticmethod
    def _register_zone(
        zone: Zone,
        zones: dict[str, Zone],
        line_num: int,
    ) -> None:
        """Add a zone to the dict, raising if the name is already taken.

        Args:
            zone:     Zone to register.
            zones:    Accumulated zones dict (mutated in place).
            line_num: For error reporting.

        Raises:
            ParseError: If the zone name is already used.
        """
        if zone.name in zones:
            raise ParseError(
                line_num,
                f"Duplicate zone name '{zone.name}'"
            )
        zones[zone.name] = zone

    @staticmethod
    def _validate_graph(zones: dict[str, Zone], line_num: int) -> None:
        """Run post-parse semantic checks on the full zone set.

        Args:
            zones:    The complete zones dict.
            line_num: Used only as a fallback for error reporting.

        Raises:
            ParseError: If start/end zone requirements are not met.
        """
        starts = [z for z in zones.values() if z.is_start]
        ends = [z for z in zones.values() if z.is_end]

        if len(starts) == 0:
            raise ParseError(line_num, "No 'start_hub' zone defined")
        if len(starts) > 1:
            names = [z.name for z in starts]
            raise ParseError(line_num, f"Multiple 'start_hub' zones: {names}")

        if len(ends) == 0:
            raise ParseError(line_num, "No 'end_hub' zone defined")
        if len(ends) > 1:
            names = [z.name for z in ends]
            raise ParseError(line_num, f"Multiple 'end_hub' zones: {names}")
