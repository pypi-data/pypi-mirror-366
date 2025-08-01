import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Queue(str, Enum):
    integrations = "integrations"
    scouty = "scouty"
    jobs = "jobs"
    insights = "insights"
    billing = "billing"
    iam = "iam"


@dataclass
class Event:
    event_type: str
    event: dict
    created_on: datetime = None

    def encode(self) -> bytes:
        self.created_on: datetime = datetime.now()
        return json.dumps(self.__dict__, default=str).encode()


@dataclass
class Message:
    body: Event
    queue: Queue
