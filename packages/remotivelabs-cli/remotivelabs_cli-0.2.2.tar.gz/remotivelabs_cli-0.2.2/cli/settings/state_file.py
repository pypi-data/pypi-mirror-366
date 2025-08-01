from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dacite import from_dict

from cli.utils.time import parse_datetime


@dataclass
class StateFile:
    version: str = "1.0"
    last_update_check_time: Optional[str] = None

    def dumps(self) -> str:
        return json.dumps(dataclasses.asdict(self), default=str)

    def should_perform_update_check(self) -> bool:
        if self.last_update_check_time:
            seconds = (datetime.now() - parse_datetime(self.last_update_check_time)).seconds
            return (seconds / 3600) > 2
        # This will solve the issue
        return True

    @staticmethod
    def loads(data: str) -> StateFile:
        d = json.loads(data)
        return from_dict(StateFile, d)
