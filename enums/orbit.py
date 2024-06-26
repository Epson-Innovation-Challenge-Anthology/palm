from enum import Enum


class DistanceType(str, Enum):
    CLOSER = "closer"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
