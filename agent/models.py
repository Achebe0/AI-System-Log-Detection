## creating the agent

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class Anamoly_Lvl(Enum):
    NORMAL = 0
    MEDIUM = 1
    CRITICAL = 2 


@dataclass
class LogEvent:
    timestamp: str
    service: str
    severity: Anamoly_Lvl
    message: str

@dataclass
class LogEvent:
    timestamp : str
    service: str
    latency_ms : int
    status_code: int
    severity: str
    msg : str
    scenario : str

@dataclass
class KowalskiAnalysis:
    log_event: LogEvent
    anamoly_level: Anamoly_Lvl
    confidence: float
    reasoning: str

@dataclass
class Action:
    action_type: str
    target: str
    desc : str
    severity: str

    