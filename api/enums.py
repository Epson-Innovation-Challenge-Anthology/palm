from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    TEST = "test"
    STAGING = "stage"
    PRODUCTION = "prod"

    def __str__(self):
        return str(self.value).upper()


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"

    def __str__(self):
        return str(self.value).upper()
