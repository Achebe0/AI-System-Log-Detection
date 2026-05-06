import json
from typing import List, Callable
from .models import LogEvent


class Monitor:

    def __init__(self, json_file : str):
        self.json_file = json_file
        self.prev_pos = 0
        self.callbacks: List[Callable[[LogEvent],None]] = []
        self.logs_seen = 0

    def register_callback(self, callback: Callable[[LogEvent],None]) -> None:




        return new_logs