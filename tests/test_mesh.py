import pytest
from fastapi.testclient import TestClient

from mesh.api import app
from mesh.queue import TaskMesh

client = TestClient(app)


def test_task_mesh() -> None:
    m = TaskMesh()
    tid = m.submit_task("resize_image", {"width": 800})
    t = m.get_task(tid)
    assert t is not None
    assert t["status"] == "COMPLETED"
    assert m.get_task("missing") is None


def test_task_mesh_priority_ordering_and_validation() -> None:
    m = TaskMesh()
    m.submit_task("low_job", {}, priority=1)
    m.submit_task("critical_job", {}, priority=10)
    m.submit_task("mid_job", {}, priority=5)

    ordered = [t["name"] for t in m.list_tasks()]
    assert ordered == ["critical_job", "mid_job", "low_job"]

    with pytest.raises(ValueError, match="empty"):
        m.submit_task("   ", {})
    with pytest.raises(ValueError, match="non-negative"):
        m.submit_task("bad_prio", {}, priority=-1)


def test_task_mesh_api() -> None:
    assert client.get("/health").json() == {"status": "ok"}

    missing = client.get("/api/v1/tasks/nonexistent")
    assert missing.status_code == 404

    created = client.post(
        "/api/v1/tasks",
        json={"name": "sync_index", "payload": {"shard": 2}, "priority": 5},
    )
    assert created.status_code == 201
    tid = created.json()["task_id"]

    fetched = client.get(f"/api/v1/tasks/{tid}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "sync_index"
    assert any(t["id"] == tid for t in client.get("/api/v1/tasks").json())
