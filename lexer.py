from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Iterator, Optional
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
        super().__init__(f"line {line}: {message}")


@dataclass
class Token:
    type: str
    raw: str
    line: int


@dataclass
class RawHub:
    kind: str
    name: str
    x: int
    y: int
    metadata: Optional[list[str]] = None


@dataclass
class RawConn:
    point_from: str
    point_to: str
    metadata: Optional[list[str]] = None


@dataclass
class RawMap:
    drones_n: int
    hubs: list[RawHub]
    conns: list[RawConn]

    def info(self) -> None:
        print(f'Drones N: {self.drones_n}')

        for hb in self.hubs:
            print(f'Hub: {hb}')

        for cn in self.conns:
            print(f'Connection: {cn}')


class Scanner:

    def __init__(self, source: str) -> None:
        self.__source = source
        self.grammar = re.compile(
            r'(?P<COMMENT>#.*)'
            r'|(?P<DRONES>nb_drones\s*:.*)'
            r'|(?P<START>start_hub\s*:.*)'
            r'|(?P<END>end_hub\s*:.*)'
            r'|(?P<HUB>hub\s*:.*)'
            r'|(?P<CONN>connection\s*:.*)'
            r'|(?P<EMPTY>\n?)'
        )

    def scan(self) -> list[Token]:
        data = self.__source.split('\n')
        tokens: list[Token] = []
        line = 1
        for line_n, line  in enumerate(data, start=1):
            mt = self.grammar.match(line)
            if mt:
                tk_type = mt.lastgroup
                tokens.append(Token(tk_type, line, line_n))
            else:
                raise ParseError('Unrecognized line', line_n)
        return tokens

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.__tokens = tokens
        self.__raw_map: RawMap = RawMap(0, [], [])

    def parse(self) -> RawMap:
        self.__raw_map = RawMap(0, [], [])
        for tk in self.__tokens:
            print(tk)
        self.__tokens = [tk for tk in self.__tokens if tk.type != 'COMMENT']
        self._parse_drones()
        self._parse_hub()
        self._parse_conns()
        self._validate()
        return self.__raw_map

    def _parse_drones(self) -> None:
        tk = self.__tokens[0]
        if tk.type != 'DRONES':
            raise ParseError("Drones not first line", tk.line)
        data = tk.raw.strip().split(':')
        num =  int(data[1])
        if num < 1:
            raise ParseError('Not enough drones', tk.line)
        self.__raw_map.drones_n = num

    def _parse_hub(self) -> None:
        hub_tks = [
            tk
            for tk in self.__tokens
            if tk.type in ['HUB', 'END', 'START']
            ]
        HUB_PATTERN = re.compile(
            r'(?:start_hub|end_hub|hub)\s*:\s*'
            r'(?P<name>\S+)\s+'
            r'(?P<x>\d+)\s+'
            r'(?P<y>\d+)'
            r'(?:\s+\[(?P<meta>[^\]]+)\])?'  # optional metadata
        )
        for tk in hub_tks:
            mt = HUB_PATTERN.match(tk.raw)
            if not mt:
                raise ParseError("Invalid hub format!", tk.line)

            rh = RawHub(
                tk.type,
                mt.group('name'),
                int(mt.group('x')),
                int(mt.group('y')),
                mt.group('meta')
                )
            self.__raw_map.hubs.append(rh)

    def _parse_conns(self) -> None:
        # Do connections here
        conn_tks = [tk for tk in self.__tokens if tk.type == 'CONN']
        CONN_PATTERN = re.compile(
            r'connection:\s*'
            r'(?P<node1>\S+)-(?P<node2>\S+)'
            r'(?:\s*\[(?P<meta>[^\]]+)\])?'
        )

        for tk in conn_tks:
            mt = CONN_PATTERN.match(tk.raw)
            if not mt:
                raise ParseError("Invalid connection format!", tk.line)

            rc = RawConn(mt.group('node1'), mt.group('node2'), mt.group('meta'))
            self.__raw_map.conns.append(rc)

    def _validate(self) -> None:
        # validate metadata
        # validate hubs
        # validate conns
        ...

if __name__ == '__main__':

    with open('linear_path.txt', 'r') as file:
        source = file.read()

    try:
        scanner = Scanner(source)
        tokens = scanner.scan()
        parser = Parser(tokens)
        raw_map = parser.parse()
        raw_map.info()
    except ParseError as pe:
        print(f'{pe}')