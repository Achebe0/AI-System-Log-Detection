import json
from typing import List, Callable
from .models import LogEvent, Anamoly_Lvl


class Monitor:

    def __init__(self, json_file : str):
        self.json_file = json_file
        self.prev_pos = 0
        self.callbacks: List[Callable[[LogEvent],None]] = []
        self.logs_seen = 0

    def register_callback(self, callback: Callable[[LogEvent],None]) -> None:
        """Register a callback to be notified of new log events"""
        self.callbacks.append(callback)

    
    def check_for_new_logs(self) -> List[LogEvent]:
        """Poll for new logs since last check"""
        new_logs = []

        try:
            with open(self.json_file, 'r') as f:
                f.seek(self.prev_pos)
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        log_event = LogEvent(**data)
                        new_logs.append(log_event)

                        # Trigger callbacks to notify reasoner of new log event
                        for callback in self.callbacks:
                            callback(log_event)

                self.prev_pos = f.tell()
                self.logs_seen += len(new_logs)
        except FileNotFoundError:
            pass

        return new_logs
