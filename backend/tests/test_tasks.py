"""Baseline CRUD tests (Modules 1-3)."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_task_defaults(client):
    r = client.post("/tasks", json={"title": "Write report"})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] > 0
    assert body["title"] == "Write report"
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["created_at"] == body["updated_at"]


def test_create_task_rejects_blank_title(client):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_list_tasks_and_filter_by_status(client):
    client.post("/tasks", json={"title": "A", "status": "todo"})
    client.post("/tasks", json={"title": "B", "status": "done"})

    all_tasks = client.get("/tasks").json()
    assert len(all_tasks) == 2

    done = client.get("/tasks", params={"status": "done"}).json()
    assert [t["title"] for t in done] == ["B"]


def test_get_task_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_update_task(client):
    task_id = client.post("/tasks", json={"title": "Draft"}).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"
    # unchanged fields survive a partial update
    assert r.json()["title"] == "Draft"


def test_delete_task(client):
    task_id = client.post("/tasks", json={"title": "Temp"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


# --- Mid-course project: due dates + overdue filter -------------------------


def test_create_task_with_valid_due_date(client):
    r = client.post("/tasks", json={"title": "Ship it", "due_date": "2099-01-01"})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == "2099-01-01"
    assert body["overdue"] is False


def test_create_task_rejects_invalid_due_date_format(client):
    r = client.post("/tasks", json={"title": "Bad date", "due_date": "01/01/2099"})
    assert r.status_code == 422


def test_task_overdue_detection(client):
    overdue = client.post(
        "/tasks", json={"title": "Late", "due_date": "2020-01-01"}
    ).json()
    assert overdue["overdue"] is True

    # done tasks are never "overdue" even with a past due date
    done_late = client.post(
        "/tasks",
        json={"title": "Late but done", "due_date": "2020-01-01", "status": "done"},
    ).json()
    assert done_late["overdue"] is False

    future = client.post(
        "/tasks", json={"title": "Future", "due_date": "2099-01-01"}
    ).json()
    assert future["overdue"] is False


def test_update_task_due_date(client):
    task_id = client.post("/tasks", json={"title": "Plan"}).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"due_date": "2030-06-01"})
    assert r.status_code == 200
    assert r.json()["due_date"] == "2030-06-01"


def test_filter_returns_only_overdue_tasks(client):
    client.post("/tasks", json={"title": "Overdue", "due_date": "2020-01-01"})
    client.post("/tasks", json={"title": "Not overdue", "due_date": "2099-01-01"})
    client.post("/tasks", json={"title": "No due date"})

    r = client.get("/tasks", params={"overdue": "true"})
    assert r.status_code == 200
    assert [t["title"] for t in r.json()] == ["Overdue"]


# --- Mid-course project: tags / labels ---------------------------------------


def test_create_task_with_tags(client):
    r = client.post("/tasks", json={"title": "Tagged", "tags": ["backend", "urgent"]})
    assert r.status_code == 201
    assert r.json()["tags"] == ["backend", "urgent"]


def test_create_task_rejects_empty_tag(client):
    r = client.post("/tasks", json={"title": "Bad tag", "tags": ["ok", "   "]})
    assert r.status_code == 422


def test_create_task_rejects_too_many_tags(client):
    r = client.post(
        "/tasks", json={"title": "Overtagged", "tags": [f"tag{i}" for i in range(11)]}
    )
    assert r.status_code == 422


def test_update_task_tags(client):
    task_id = client.post("/tasks", json={"title": "Retag"}).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"tags": ["frontend"]})
    assert r.status_code == 200
    assert r.json()["tags"] == ["frontend"]


def test_filter_by_tag(client):
    client.post("/tasks", json={"title": "A", "tags": ["backend"]})
    client.post("/tasks", json={"title": "B", "tags": ["frontend"]})

    r = client.get("/tasks", params={"tag": "backend"})
    assert r.status_code == 200
    assert [t["title"] for t in r.json()] == ["A"]


def test_update_task_preserves_tags_after_unrelated_update(client):
    task_id = client.post(
        "/tasks", json={"title": "Keep tags", "tags": ["keep-me"]}
    ).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["tags"] == ["keep-me"]
