from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.config import today


def test_crud(client: TestClient) -> None:
    assert client.get("/api/tasks").json() == []
    response = client.post("/api/tasks", json={"title": "  Pythonを学ぶ  "})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Pythonを学ぶ"
    assert task["created_at"].endswith("Z")
    task_id = task["id"]
    assert client.get(f"/api/tasks/{task_id}").json() == task
    assert len(client.get("/api/tasks").json()) == 1
    update = client.patch(
        f"/api/tasks/{task_id}",
        json={
            "title": "更新",
            "description": "詳細",
            "priority": "high",
            "due_date": "2027-01-01",
            "is_completed": True,
        },
    )
    assert update.status_code == 200
    assert update.json()["is_completed"] is True
    assert update.json()["updated_at"] >= task["updated_at"]
    assert client.patch(f"/api/tasks/{task_id}", json={"due_date": None}).json()["due_date"] is None
    assert client.patch(f"/api/tasks/{task_id}", json={}).status_code == 200
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": "x" * 101},
        {"title": None},
        {"title": 123},
        {"title": "ok", "priority": "urgent"},
        {"title": "ok", "priority": None},
        {"title": "ok", "description": "x" * 1001},
        {"title": "ok", "due_date": "2026-02-30"},
        {"title": "ok", "due_date": 123},
        {"title": "ok", "is_completed": True},
        {"title": "ok", "unknown": "bad"},
    ],
)
def test_invalid_create(client: TestClient, body: dict[str, object]) -> None:
    assert client.post("/api/tasks", json=body).status_code == 422


@pytest.mark.parametrize(
    "body",
    [
        {"title": None},
        {"description": None},
        {"priority": None},
        {"is_completed": None},
        {"is_completed": "false"},
        {"title": " "},
        {"priority": "urgent"},
    ],
)
def test_invalid_patch(client: TestClient, body: dict[str, object]) -> None:
    task_id = client.post("/api/tasks", json={"title": "original"}).json()["id"]
    assert client.patch(f"/api/tasks/{task_id}", json=body).status_code == 422
    assert client.get(f"/api/tasks/{task_id}").json()["title"] == "original"


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing(client: TestClient, method: str) -> None:
    assert (
        client.request(
            method, "/api/tasks/999", **({"json": {}} if method == "patch" else {})
        ).status_code
        == 404
    )


def test_stats_filter_sort_and_overdue(client: TestClient) -> None:
    yesterday = (today() - timedelta(days=1)).isoformat()
    for title, priority, due in [
        ("low", "low", None),
        ("high", "high", yesterday),
        ("medium", "medium", today().isoformat()),
    ]:
        result = client.post(
            "/api/tasks", json={"title": title, "priority": priority, "due_date": due}
        )
        assert result.json()["is_overdue"] == (title == "high")
    assert client.get("/api/tasks/stats").json() == {
        "total": 3,
        "completed": 0,
        "pending": 3,
        "overdue": 1,
    }
    assert [t["title"] for t in client.get("/api/tasks?sort=priority").json()] == [
        "high",
        "medium",
        "low",
    ]
    ordered = client.get("/api/tasks?sort=due_date").json()
    assert [t["title"] for t in ordered] == ["high", "medium", "low"]
    task_id = ordered[0]["id"]
    result = client.patch(f"/api/tasks/{task_id}", json={"is_completed": True})
    assert not result.json()["is_overdue"]
    assert len(client.get("/api/tasks?status=completed").json()) == 1
    assert len(client.get("/api/tasks?status=pending").json()) == 2
    assert client.get("/api/tasks/stats").json() == {
        "total": 3,
        "completed": 1,
        "pending": 2,
        "overdue": 0,
    }
    assert client.get("/api/tasks?sort=bad").status_code == 422
    assert client.get("/api/tasks?status=bad").status_code == 422


def test_static_health_docs_security(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    page = client.get("/")
    assert page.status_code == 200
    assert "TaskFlow" in page.text
    assert "frame-ancestors 'none'" in page.headers["content-security-policy"]
    assert client.get("/static/js/app.js").status_code == 200
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_boundaries_and_xss_storage(client: TestClient) -> None:
    title = "<script>alert(1)</script>"
    result = client.post("/api/tasks", json={"title": title, "description": "x" * 1000})
    assert result.status_code == 201
    assert result.json()["title"] == title
    assert "innerHTML" not in client.get("/static/js/app.js").text
    assert client.post("/api/tasks", json={"title": "あ" * 100}).status_code == 201
