from enum import Enum


class Sex(str, Enum):
    MALE: str = "M"
    FEMALE: str = "F"
    OTHER: str = "O"
