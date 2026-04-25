from enum import Enum


class Service(Enum):
    AUTH = "auth_service"
    DATABASE = "database_service"
    API = "api_service"


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Scenario(Enum):
    NORMAL = "NORMAL"
    DB_LATENCY = "DB_LATENCY"
    AUTH_FAILURE = "AUTH_FAILURE"
    TRAFFIC_SPIKE = "TRAFFIC_SPIKE"
    DEGRADATION = "DEGRADATION"


class Intensity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
