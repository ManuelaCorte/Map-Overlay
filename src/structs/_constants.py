from enum import Enum

EPS = 1e-8


class EventType(Enum):
    START = 1
    INTERSECTION = 2
    END = 3
