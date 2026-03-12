import time
from collections import deque
from typing import Optional


class LogEntry:
    __slots__ = (
        "timestamp",
        "model",
        "token_name",
        "stream",
        "status",
        "duration",
        "error",
    )

    def __init__(
        self,
        model: str,
        token_name: str,
        stream: bool,
        status: str = "pending",
        duration: float = 0,
        error: str = "",
    ):
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.model = model
        self.token_name = token_name
        self.stream = stream
        self.status = status
        self.duration = round(duration, 2)
        self.error = error

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "model": self.model,
            "token_name": self.token_name,
            "stream": self.stream,
            "status": self.status,
            "duration": self.duration,
            "error": self.error,
        }


class LogStore:
    def __init__(self, max_entries: int = 500):
        self._logs: deque[LogEntry] = deque(maxlen=max_entries)
        self.total_requests: int = 0
        self.total_success: int = 0
        self.total_errors: int = 0

    def add(self, entry: LogEntry):
        self._logs.appendleft(entry)
        self.total_requests += 1
        if entry.status == "success":
            self.total_success += 1
        elif entry.status == "error":
            self.total_errors += 1

    def resize(self, max_entries: int):
        old = list(self._logs)
        self._logs = deque(old, maxlen=max_entries)

    def query(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        items = list(self._logs)
        if status:
            items = [e for e in items if e.status == status]
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [e.to_dict() for e in items[start:end]],
        }
