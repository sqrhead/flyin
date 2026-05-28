"""Parser module for reading and validating drone routing map files."""

from __future__ import annotations

import os
from typing import Optional, cast


from graph import Connection, Graph, Zone, ZoneType


class ParseError(Exception):
    """Raised when the map file contains invalid syntax or structure."""

    def __init__(self, message: str, line: int) -> None:
        """Initialize a ParseError with a message and line number.

        Args:
            message: Human-readable description of the error.
            line: Line number in the source file where the error occurred.
        """
        super().__init__(f"Line {line}: {message}")


class Parser:
    """Parses a drone routing map file into a Graph object."""

    def __init__(self, filepath: str) -> None:
        """Initialize the Parser with a file path.

        Args:
            filepath: Path to the map file to parse.
        """
        self.__filepath: str = filepath

    def parse(self) -> Optional[Graph]:
        """Parse the map file and return a Graph.

        Returns:
            A populated Graph on success, or Graph(-1, [], []) on error.
        """
        lines: list[str] = []
        try:
            with open(self.__filepath, "r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            raise ParseError("Error: File name is wrong", 0)
        try:
            graph = self._process(lines)
            return graph
        except ParseError as pe:
            print(f"{pe}")
            os._exit(1)

    def _process(self, lines: list[str]) -> Graph:
        """Process all lines and build the Graph.

        Args:
            lines: Raw lines from the map file.

        Returns:
            A fully constructed and validated Graph.

        Raises:
            ParseError: If any line is malformed or constraints are violated.
        """
        nb_drones: Optional[int] = None
        zones: list[Zone] = []
        zone_lines: list[int] = []
        connections: list[Connection] = []
        conn_lines: list[int] = []

        for line_nb, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones"):
                if nb_drones is not None:
                    raise ParseError("Duplicate nb_drones", line_nb)
                nb_drones = self._process_drones(line=line, line_nb=line_nb)
            elif (
                line.startswith("start_hub:")
                or line.startswith("end_hub:")
                or line.startswith("hub:")
            ):
                if nb_drones is None:
                    raise ParseError(
                        "nb_drones not found as first line", line_nb
                    )
                zones.append(self._process_zone(line, line_nb))
                zone_lines.append(line_nb)
            elif line.startswith("connection"):
                if nb_drones is None:
                    raise ParseError(
                        "nb_drones not found as first line", line_nb
                    )
                connections.append(self._process_connection(line, line_nb))
                conn_lines.append(line_nb)
            else:
                raise ParseError("ParseError: Line wrong format", line_nb)

        if nb_drones is None:
            raise ParseError("ParseError: nb_drones not defined", 0)
        self._validate_zones(zones, zone_lines)
        self._validate_connections(zones, connections, conn_lines)
        return Graph(nb_drones, zones, connections)

    def _process_drones(self, line: str, line_nb: int) -> int:
        """Parse the nb_drones line.

        Args:
            line: The raw line string.
            line_nb: Line number for error reporting.

        Returns:
            The number of drones as a positive integer.

        Raises:
            ParseError: If the format or value is invalid.
        """
        parts = line.split(":", 1)
        if len(parts) < 2:
            raise ParseError("Wrong drone format: nb_drones:<int>", line_nb)
        if not parts[1].strip().isdigit():
            raise ParseError("Drones must be a valid integer", line_nb)
        drones = int(parts[1])
        if drones <= 0:
            raise ParseError("Drones must be > 0", line_nb)

        return drones

    def _process_zone(self, line: str, line_nb: int) -> Zone:
        """Parse a hub/start_hub/end_hub line into a Zone.

        Args:
            line: The raw line string.
            line_nb: Line number for error reporting.

        Returns:
            A Zone object with all fields set.

        Raises:
            ParseError: If the format or any value is invalid.
        """
        zone_format = "tag: name coord_x coord_y [metadata_k=metadata_v]"
        is_start: bool = False
        is_end: bool = False
        name: Optional[str] = None
        coord_x: Optional[int] = None
        coord_y: Optional[int] = None
        zone_type: ZoneType = ZoneType.NORMAL
        max_drones: int = 1
        color: Optional[str] = None

        data = line.strip().split(":", 1)
        if len(data) < 2:
            raise ParseError("Missing colon separator after zone tag", line_nb)

        tag = data[0].lower().strip()

        if tag == "start_hub":
            is_start = True
        elif tag == "end_hub":
            is_end = True
        elif tag != "hub":
            raise ParseError("Invalid zone tag", line_nb)

        rest = data[1]

        has_bracket = "[" in rest or "]" in rest
        if has_bracket:
            if "[" not in rest or "]" not in rest:
                raise ParseError("Metadata: missing closing bracket", line_nb)
            ob_index = rest.find("[")
            cb_index = rest.find("]")
            if len(rest) > cb_index + 2:
                raise ParseError("Data after metadata", line_nb)
            metadata_raw = rest[ob_index:cb_index + 1]
            coords_part = rest[:ob_index].strip()
        else:
            metadata_raw = "[]"
            coords_part = rest.strip()

        coords = coords_part.split()
        if len(coords) != 3:
            raise ParseError(
                f"Wrong zone format, accepted: {zone_format}", line_nb
            )

        name = coords[0].strip()
        if " " in name or "-" in name:
            raise ParseError("Dash or Space in Zone name", line_nb)

        raw_x = coords[1].strip()
        raw_y = coords[2].strip()

        # Validate that coordinates are valid integers (may be negative).
        try:
            coord_x = int(raw_x)
            coord_y = int(raw_y)
        except ValueError:
            raise ParseError(
                f"Coords must be valid integers, got '{raw_x}' '{raw_y}'",
                line_nb
            )

        metadata_content = metadata_raw[1:len(metadata_raw) - 1].strip()

        for token in metadata_content.split():
            if "=" not in token:
                raise ParseError(
                    f"Wrong metadata format '{token}', "
                    f"expected key=value", line_nb
                )
            parts = token.split("=", 1)
            key = parts[0].strip().lower()
            value = parts[1].strip()

            if key == "color":
                color_ln = value.lower()
                if not color_ln.isalpha():
                    raise ParseError(
                        "Metadata: Color is not a single word", line_nb)
                color = color_ln
            elif key == "zone":
                zone_ln = value.lower()
                if zone_ln not in [
                    "normal", "blocked", "restricted", "priority"
                        ]:
                    raise ParseError("Metadata Zone not available", line_nb)
                zone_type = ZoneType(zone_ln)
            elif key == "max_drones":
                if not value.isdigit():
                    raise ParseError(
                        "Metadata MaxDrones not valid integer", line_nb
                    )
                md_value = int(value)
                if md_value <= 0:
                    raise ParseError("Metadata MaxDrones <= 0", line_nb)
                max_drones = md_value

        return Zone(
            name,
            coord_x, coord_y,
            zone_type, color, max_drones,
            is_start, is_end
        )

    def _process_connection(self, line: str, line_nb: int) -> Connection:
        """Parse a connection line into a Connection.

        Args:
            line: The raw line string.
            line_nb: Line number for error reporting.

        Returns:
            A Connection object.

        Raises:
            ParseError: If the format or any value is invalid.
        """
        max_link_capacity: int = 1
        data = line.strip().split(":", 1)
        if len(data) < 2:
            raise ParseError(
                "Connection line missing colon separator", line_nb)
        if data[0].lower().strip() != "connection":
            raise ParseError("Connection wrong tag [connection]", line_nb)

        rest = data[1].strip()
        ob_index = rest.find("[")
        cb_index = rest.find("]")

        if ob_index > 0 and cb_index == -1:
            raise ParseError("Metadata wrong format", line_nb)
        if ob_index == -1 and cb_index > 0:
            raise ParseError("Metadata wrong format", line_nb)
        if cb_index > -1 and len(rest) > cb_index + 2:
            raise ParseError("Metadata wrong format", line_nb)

        metadata_raw = rest[ob_index:cb_index + 1] if ob_index >= 0 else ""
        if metadata_raw:
            rest = rest.removesuffix(metadata_raw).strip()

        parts = rest.split("-", 1)
        if len(parts) != 2:
            raise ParseError("Connection wrong format", line_nb)

        zone_a = parts[0].strip()
        zone_b = parts[1].strip()

        if " " in zone_a:
            raise ParseError("Connection zone name contains space", line_nb)
        if " " in zone_b:
            raise ParseError("Connection zone name contains space", line_nb)

        if metadata_raw:
            metadata_content = metadata_raw[1:len(metadata_raw) - 1]
            for token in metadata_content.split():
                if "=" not in token:
                    raise ParseError("Metadata wrong format", line_nb)
                kv = token.split("=", 1)
                if len(kv) != 2:
                    raise ParseError("Metadata wrong format", line_nb)
                if kv[0].strip().lower() == "max_link_capacity":
                    if not kv[1].strip().isdigit():
                        raise ParseError("Metadata wrong value", line_nb)
                    max_link_capacity = int(kv[1].strip())
                    if max_link_capacity < 1:
                        raise ParseError("Metadata: data not valid", line_nb)

        return Connection(zone_a, zone_b, max_link_capacity)

    def _validate_zones(
            self,
            zones: list[Zone],
            zones_lines: list[int]) -> None:
        """Validate that zones list has exactly one start and one end.

        Args:
            zones: List of parsed zones.

        Raises:
            ParseError: If names are duplicated, or start/end count != 1.
        """
        if not zones:
            raise ParseError("No zones or hubs defined in the map file", 1)
        start_count: int = 0
        end_count: int = 0
        names: list[str] = []

        for i, zone in enumerate(zones):
            line_nb = zones_lines[i]
            if zone.name in names:
                raise ParseError("Zone not unique name", line_nb)
            names.append(zone.name)
            if zone.is_start:
                start_count += 1
            if zone.is_end:
                end_count += 1

        if start_count == 0:
            raise ParseError("No start_hub defined", line_nb)
        if start_count > 1:
            raise ParseError("Multiple start_hub zones defined", line_nb)
        if end_count == 0:
            raise ParseError("No end_hub defined", line_nb)
        if end_count > 1:
            raise ParseError("Multiple end_hub zones defined", line_nb)

    def _validate_connections(
        self,
        zones: list[Zone],
        connections: list[Connection],
        conn_lines: list[int]
    ) -> None:
        """Validate that all connections.

        Args:
            zones: List of parsed zones.
            connections: List of parsed connections.

        Raises:
            ParseError: If a connection references an unknown zone, is a
                        self-loop, or is duplicated.
        """
        prev_connections: set[tuple[str, str]] = set()
        zone_names = {z.name for z in zones}

        for i, conn in enumerate(connections):
            line_nb = conn_lines[i]
            if conn.zone_a not in zone_names or conn.zone_b not in zone_names:
                raise ParseError(
                    f"Connection links dont exist: {conn.zone_a} - "
                    f"{conn.zone_b}", line_nb
                )
            if conn.zone_a == conn.zone_b:
                raise ParseError(
                    f"Connection loop -> {conn.zone_a} - "
                    f"{conn.zone_b}", line_nb
                )
            pair = cast(
                tuple[str, str],
                tuple(sorted((conn.zone_a, conn.zone_b))))
            if pair in prev_connections:
                raise ParseError(
                    f"Connection {conn.zone_a} - "
                    f"{conn.zone_b} already exists", line_nb
                )
            prev_connections.add(pair)
