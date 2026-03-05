from dataclasses import dataclass
from enum import Enum

# Token Type
class TokenType(Enum):
    NB_DRONES = 0
    HUB = 1
    CONNECTION = 2
    ...


@dataclass
class Token:
    line_number: int
    token_type: TokenType
    raw_value: str


@dataclass
class RawZone:
    name: str
    x: int
    y: int
    metadata: dict[str, str]
    line_number: int  # For error purpose

# Raw -> Token -> Parser -> Validator -> Result
# TODO: Find a guide on how this works better
# Pydantic fucking useless

