from __future__ import annotations
import re
from typing import Optional
from graph import Graph, Zone, Connection, ZoneType
from vars import *
'''
Constraints:
    -- First line must define number of drones [!]
    -- Any numbers of drones permitted [v]
    -- One start hub and one end hub []
    -- Each zone must have a unique name and valid integers coords
    -- Zones name can have any type of valid chars excluded spaces and dashes
    -- Connections must link only previous declared zones
    -- The same connect cant appear twice
    -- Metadata has to be sintatically valid (ex: name=...)
    -- Capacity values must be positive integers
    -- Any other parsing error must stop the program and return a clear error message
        indicating the line and cause

# TODO: Find a guide on how this works better
# Raw -> Token -> Parser -> Validator -> Result
'''
# SCANNER -> TOKENIZER -> PARSER -> RAW__MAP
'''
SCANNER :
    Scans the file, and creates token of the file
TOKENIZER:
    Regex of desired format, and Token class
PARSER:
    Takes tokens and creates a RawMap, or raise ParserError
'''
'''
PROBLEMS:
    At the moment i feel like validation is kinda disconnected from the rest of the pipeline

'''

class ParseError(Exception):
    def __init__(self, message: str, line: int) -> None:
        super().__init__(f"Line {line}: {message}")

class Parser:
    def __init__(self, filepath: str) -> None:
        self.__filepath = filepath

    def parse(self) -> Graph:
        with open(self.__filepath, 'r') as file:
            lines = file.readlines()

        return self._process(lines)

    def parse_debug(self) -> None:
        try:
            print(
                self._process_zone("hub: name 1 1 [color=green]", 99)
                )
            print(
                self._process_connection(
                    "connection: name1-name2 [max_link_capacity=10]",
                    99
                    )
                )
            print("Validate Zones: ", self._validate_zones())
        except ParseError as pe:
            print(f'{pe}')

    def _process(self, lines: list[str]) -> Graph:
        nb_drones: Optional[int] = None
        zones: list[Zone] = []
        connections: list[Connection] = []

        for line_nb, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            if not line or line.startswith('#'):
                continue

            if line.startswith('nb_drones'):
                if nb_drones is not None:
                    raise ParseError('Duplicate nb_drones', line_nb)
                nb_drones = self._process_drones(line=line)
            elif 'hub' in line:
                if nb_drones is None:
                    raise ParseError("nb_drones not found as first line", line_nb)
                zones.append(self._process_zone(line, line_nb))
            elif line.startswith('connection'):
                if nb_drones is None:
                    raise ParseError("nb_drones not found as first line", line_nb)
                connections.append(self._process_connection(line, line_nb))
            else:
                
                raise ParseError('ParseError: Line wrong format', line_nb)

        return Graph(nb_drones, zones, connections)


    def _process_drones(self, line: str, line_nb: int) -> int:
        parts = line.split(':', 1)
        if len(parts) < 2:
            raise ParseError('Wrong drone format: nb_drones:<int>', line_nb)
        if not parts[1].strip().isdigit():
            raise ParseError('Drones must be a valid integer', line_nb)
        drones = int(parts[1])
        if drones <= 0:
            raise ParseError('Drones must be > 0', line_nb)
        return drones

    def _process_zone(self, line: str, line_nb: int) -> Zone:
        # tag: name coord_x coord_y [metadata_k=metadata_v]
        zone_format = 'tag: name coord_x coord_y [metadata_k=metadata_v]'
        is_start: bool = False
        is_end: bool = False
        name: str = None
        coord_x: int = None
        coord_y: int = None
        zone_type = ZoneType.NORMAL
        max_drones = 1
        color = None

        data = line.strip().split(':', 1)
        tag = data[0].lower().strip()
        # Check if is end or start
        if tag in ['start_hub', 'hub', 'end_hub']:
            if tag == "start_hub":
                if is_start == True:
                    raise ParseError("Duplicate Start Hub", line_nb)
                is_start = True
            if tag == "end_hub":
                if is_end == True:
                    raise ParseError("Duplicate End Hub", line_nb)
                is_end = True
        else:
            raise ParseError("Invalid zone tag", line_nb)

        if not '[' in data[1] or not "]" in data[1]:
            raise ParseError('Metadata: missing brackets', line_nb)
        # find metadata indexes
        ob_index = data[1].find("[")
        cb_index = data[1].find("]")
        metadata = data[1][ob_index:cb_index+1]

        if len(data[1]) > cb_index + 2:
            raise ParseError("Data after metadata", line_nb)

        # remove suffix (metadata)
        data[1] = data[1].removesuffix(metadata)
        data = data[1].split()

        if len(data) != 3:
            raise ParseError(f'Wrong zone format, accepted: {zone_format}', line_nb)

        name = data[0].strip()
        if ' ' in name or '-' in name:
            raise ParseError('Dash or Space in Zone name', line_nb)
        coord_x = data[1].strip()
        coord_y = data[2].strip()
        if not coord_x.strip().isdigit() or not coord_y.strip().isdigit():
            raise ParseError(f'Coords must be valid integers, {coord_x} {coord_y}', line_nb)
        coord_x = int(coord_x)
        coord_y = int(coord_y)
        if coord_x < 0 or coord_y < 0:
            raise ParseError('Coords must be positive integers', line_nb)

        # remove start and end of the string ( [] )
        metadata = metadata[1:len(metadata)-1].strip()
        metadata = metadata.split()
        # validate and set metadata
        for line in metadata:
            if not '=' in line:
                raise ParseError('Wrong metadata format, <key>=<value>', line_nb)
            line = line.split('=', 1)
            if len(line) != 2:
                raise ParseError(f'{line} : wrong metadata format', line_nb)
            # more metadata key-value are not inserted
            match (line[0].strip().lower()):
                case 'color':
                    color_ln = line[1].strip().lower()
                    if not color_ln in AVB_COLORS:
                        raise ParseError('Metadata: Color not avaible', line_nb)
                    color = color_ln

                case 'zone':
                    zone_ln = line[1].strip().lower()
                    if not zone_ln in ['normal','blocked','restricted', 'priority']:
                        raise ParseError('Metadata: Zone not avaible', line_nb)
                    zone_type = ZoneType(zone_ln)

                case 'max_drones':
                    max_drones_ln = line[1].strip().lower()
                    if not max_drones_ln.isdigit():
                        raise ParseError('Metadata: MaxDrones not valid integer', line_nb)
                    value = int(max_drones_ln)
                    if value <= 0:
                        raise ParseError('Metadata: MaxDrones <= 0', line_nb)
                    max_drones = value

        return Zone(name, coord_x, coord_y, zone_type, color, max_drones, is_start, is_end)

    # Error: something after name is considered part of the name
    def _process_connection(self, line: str, line_nb: int) -> Connection:
        max_link_capacity: int = 1
        zone_a: str = None
        zone_b: str = None
        data = line.strip().split(":", 1)
        if data[0].lower().strip() != "connection":
            raise ParseError("Connection: wrong tag [connection]", line_nb)
        data = data[1].strip()
        ob_index = data.find("[")
        cb_index = data.find("]") + 1

        if ob_index > 0 and cb_index == -1:
            raise ParseError("Metadata: wrong format", line_nb)

        if ob_index == -1 and cb_index > 0:
            raise ParseError("Metadata: wrong format", line_nb)

        if len(data) > cb_index + 2:
            raise ParseError("Metadata: wrong format", line_nb)

        metadata = data[ob_index:cb_index + 1]
        # error here
        if metadata:
            data = data.removesuffix(metadata).strip()
        data = data.split("-", 1)
        if len(data) != 2:
            raise ParseError("Connection: wrong format", line_nb)

        if " " in data[0].strip():
            raise ParseError("Connection: name wrong", line_nb)
        if " " in data[1].strip():
            raise ParseError("Connection: name wrong", line_nb)

        zone_a = data[0]
        zone_b = data[1]

        metadata = metadata[1:len(metadata) - 1]
        metadata = metadata.split()

        for line in metadata:
            if not "=" in line:
                raise ParseError("Metadata: wrong format", line_nb)
            line = line.split("=")
            if len(line) != 2:
                raise ParseError("Metadata: wrong format", line_nb)

            if line[0].strip().lower() == "max_link_capacity":
                if line[1].strip().isdigit():
                    max_link_capacity = int(line[1])
                    print(max_link_capacity)
                    if max_link_capacity < 1:
                        raise ParseError("Metadata: data not valid", line_nb)
                else:
                    raise ParseError("Metadata: wrong value", line_nb)
        return Connection(zone_a, zone_b, max_link_capacity)



    def _validate_zones(self, zones) -> bool:
        has_start: bool = False
        has_end: bool = False
        names: list[str] = [n for n in self.]

        return True

        ...
    def _validate_connections(self) -> bool:
        ...


# todo : zone name bug -> no space accepted after tag
if __name__ == '__main__':
    parser = Parser('ok')
    parser.parse_debug()

