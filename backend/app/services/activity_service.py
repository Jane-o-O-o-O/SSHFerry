"""In-memory activity feed for authenticated users."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import Lock
import time


DEFAULT_ACTIVITY_BUFFER_LIMIT = 1000


@dataclass(frozen=True, slots=True)
class ActivityEntry:
    """Single user-visible activity event."""

    sequence: int
    timestamp: float
    user_id: str | None
    level: str
    category: str
    action: str
    title: str
    message: str


@dataclass(frozen=True, slots=True)
class ActivitySnapshot:
    """Snapshot of activity events for one authenticated user."""

    items: list[ActivityEntry]
    total: int
    sequence: int


class ActivityService:
    """Thread-safe ring buffer for user-scoped activity events."""

    def __init__(self, max_entries: int = DEFAULT_ACTIVITY_BUFFER_LIMIT):
        self._entries: deque[ActivityEntry] = deque(maxlen=max_entries)
        self._sequence = 0
        self._lock = Lock()

    def publish(
        self,
        *,
        user_id: str | None,
        level: str,
        category: str,
        action: str,
        title: str,
        message: str,
    ) -> ActivityEntry:
        """Append one activity event to the feed."""
        with self._lock:
            self._sequence += 1
            entry = ActivityEntry(
                sequence=self._sequence,
                timestamp=time.time(),
                user_id=user_id,
                level=level,
                category=category,
                action=action,
                title=title,
                message=message,
            )
            self._entries.append(entry)
            return entry

    def snapshot(self, *, user_id: str | None, limit: int | None = None) -> ActivitySnapshot:
        """Return the current activity feed for one user."""
        with self._lock:
            items = [item for item in self._entries if item.user_id in (None, user_id)]
            if limit is not None and limit > 0 and len(items) > limit:
                items = items[-limit:]
            return ActivitySnapshot(items=items, total=len(items), sequence=self._sequence)

    def close(self) -> None:
        """Release any held resources."""
        return None
