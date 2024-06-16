from enum import Enum


class Sex(str, Enum):
    MALE: str = "M"
    FEMALE: str = "F"
    OTHER: str = "O"


class Plan(str, Enum):
    BASIC = "BASIC"
    BEGINNER = "BEGINNER"
    EXPERT = "EXPERT"
    MASTER = "MASTER"


PLAN_MAP = {
    Plan.BASIC: 1,
    Plan.BEGINNER: 2,
    Plan.EXPERT: 3,
    Plan.MASTER: 4,
}
