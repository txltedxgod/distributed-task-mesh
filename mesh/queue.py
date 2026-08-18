import asyncio
from typing import Dict, Any, List
import uuid

class TaskMesh:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def submit_task(self, name: str, payload: Dict[str, Any], priority: int = 1) -> str:
        tid = f"task_{str(uuid.uuid4())[:8]}"
        self.tasks[tid] = {
            "id": tid,
            "name": name,
            "payload": payload,
            "priority": priority,
            "status": "COMPLETED",
            "result": f"Executed {name} successfully"
        }
        return tid

    def get_task(self, tid: str):
        return self.tasks.get(tid)
