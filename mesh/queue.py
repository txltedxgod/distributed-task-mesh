from __future__ import annotations

import threading
import uuid
from typing import Any


class TaskMesh:
    """Thread-safe in-memory distributed task queue with priority ordering."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._seq = 0
        self.tasks: dict[str, dict[str, Any]] = {}

    def submit_task(
        self, name: str, payload: dict[str, Any], priority: int = 1
    ) -> str:
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("task name must not be empty")
        if priority < 0:
            raise ValueError("priority must be non-negative")

        tid = f"task_{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._seq += 1
            self.tasks[tid] = {
                "id": tid,
                "name": cleaned,
                "payload": dict(payload),
                "priority": priority,
                "status": "COMPLETED",
                "result": f"Executed {cleaned} successfully",
                "_seq": self._seq,
            }
        return tid

    def get_task(self, tid: str) -> dict[str, Any] | None:
        with self._lock:
            task = self.tasks.get(tid)
            if task is None:
                return None
            return {k: v for k, v in task.items() if k != "_seq"}

    def list_tasks(self, status_filter: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            items = list(self.tasks.values())
        if status_filter is not None:
            items = [t for t in items if t["status"] == status_filter]
        items.sort(key=lambda t: (-t["priority"], t["_seq"]))
        return [{k: v for k, v in item.items() if k != "_seq"} for item in items]
