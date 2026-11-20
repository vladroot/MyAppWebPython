"""Thread-safe, capacity-limited message log (mirrors C# ServerMessageLog)."""

import asyncio
from collections import deque
from typing import Iterable, List


class ServerMessageLog:
    """Append-only log of responses served by /watch. Thread-safe via asyncio lock."""

    CAPACITY = 200

    def __init__(self) -> None:
        self._messages: deque[str] = deque(maxlen=self.CAPACITY)
        self._lock = asyncio.Lock()

    def add(self, message: str) -> None:
        """Add a message (synchronous, safe for use outside async context)."""
        self._messages.append(message)
        # deque(maxlen=...) automatically drops oldest entries when full.

    def snapshot(self) -> List[str]:
        """Return a copy of all current messages."""
        return list(self._messages)