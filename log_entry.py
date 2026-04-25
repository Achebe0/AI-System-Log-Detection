"""Log entry data model"""

from dataclasses import dataclass, asdict
from datetime import datetime
from constants import Service, Severity, Scenario
import json


@dataclass
class LogEntry:
    timestamp: str
    service: str
    latency_ms: int
    status_code: int
    severity: str
    message: str
    scenario: str
    
    def to_jsonl(self) -> str:
        """Convert to JSONL format"""
        return json.dumps(asdict(self))
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
