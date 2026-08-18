from mesh.queue import TaskMesh

def test_task_mesh():
    m = TaskMesh()
    tid = m.submit_task("resize_image", {"width": 800})
    t = m.get_task(tid)
    assert t["status"] == "COMPLETED"
