from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from mesh.queue import TaskMesh

app = FastAPI(title="Distributed Task Mesh", version="0.1.0")
mesh = TaskMesh()

class TaskReq(BaseModel):
    name: str
    payload: Dict[str, Any]
    priority: int = 1

@app.post("/api/v1/tasks")
def submit(req: TaskReq):
    tid = mesh.submit_task(req.name, req.payload, req.priority)
    return {"task_id": tid, "status": "QUEUED"}

@app.get("/api/v1/tasks/{tid}")
def get_status(tid: str):
    return mesh.get_task(tid)
