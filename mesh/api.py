from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from mesh.queue import TaskMesh

app = FastAPI(title="Distributed Task Mesh", version="0.1.0")
mesh = TaskMesh()


class TaskReq(BaseModel):
    name: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=0, le=100)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/tasks", status_code=status.HTTP_201_CREATED)
def submit(req: TaskReq) -> dict[str, str]:
    try:
        tid = mesh.submit_task(req.name, req.payload, req.priority)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return {"task_id": tid, "status": "QUEUED"}


@app.get("/api/v1/tasks")
def list_all(
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[dict[str, Any]]:
    return mesh.list_tasks(status_filter=status_filter)


@app.get("/api/v1/tasks/{tid}")
def get_status(tid: str) -> dict[str, Any]:
    task = mesh.get_task(tid)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task
