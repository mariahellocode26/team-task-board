"""Tests for the /tasks endpoints against openapi.yaml's contract."""

from __future__ import annotations

from fastapi.testclient import TestClient


def create(client: TestClient, **overrides) -> dict:
    body = {"title": "A task", **overrides}
    response = client.post("/tasks", json=body)
    assert response.status_code == 201, response.text
    return response.json()


class TestSeedData:
    def test_seed_data_is_present_on_startup(self, seeded_client: TestClient) -> None:
        response = seeded_client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 4
        assert {t["status"] for t in tasks} == {"todo", "in_progress", "done"}


class TestListTasks:
    def test_empty_store_returns_empty_list(self, client: TestClient) -> None:
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_tasks(self, client: TestClient) -> None:
        create(client, title="First")
        create(client, title="Second")
        response = client.get("/tasks")
        titles = {t["title"] for t in response.json()}
        assert titles == {"First", "Second"}


class TestCreateTask:
    def test_minimal_task_gets_defaults(self, client: TestClient) -> None:
        task = create(client, title="Write the report")
        assert task["title"] == "Write the report"
        assert task["priority"] == "medium"
        assert task["status"] == "todo"
        assert task["order"] == 0
        assert task["description"] is None
        assert task["assignee"] is None
        assert task["dueDate"] is None
        assert task["id"]

    def test_all_fields_round_trip(self, client: TestClient) -> None:
        task = create(
            client,
            title="Ship the release",
            description="Cut the changelog first",
            assignee="Priya",
            priority="high",
            dueDate="2026-10-01",
            status="in_progress",
        )
        assert task["description"] == "Cut the changelog first"
        assert task["assignee"] == "Priya"
        assert task["priority"] == "high"
        assert task["dueDate"] == "2026-10-01"
        assert task["status"] == "in_progress"

    def test_missing_title_is_rejected(self, client: TestClient) -> None:
        response = client.post("/tasks", json={})
        assert response.status_code == 400
        assert "message" in response.json()

    def test_blank_title_is_rejected(self, client: TestClient) -> None:
        response = client.post("/tasks", json={"title": "   "})
        assert response.status_code == 400

    def test_invalid_priority_is_rejected(self, client: TestClient) -> None:
        response = client.post("/tasks", json={"title": "X", "priority": "urgent"})
        assert response.status_code == 400

    def test_tasks_append_to_end_of_their_column(self, client: TestClient) -> None:
        first = create(client, title="First", status="todo")
        second = create(client, title="Second", status="todo")
        third = create(client, title="Third", status="done")

        assert first["order"] == 0
        assert second["order"] == 1
        # A different column starts its own sequence from 0.
        assert third["order"] == 0


class TestUpdateTask:
    def test_updates_requested_fields_only(self, client: TestClient) -> None:
        task = create(client, title="Original", priority="low")
        response = client.patch(f"/tasks/{task['id']}", json={"priority": "high"})
        assert response.status_code == 200
        updated = response.json()
        assert updated["priority"] == "high"
        assert updated["title"] == "Original"

    def test_can_clear_an_optional_field(self, client: TestClient) -> None:
        task = create(client, title="Original", assignee="Sam")
        response = client.patch(f"/tasks/{task['id']}", json={"assignee": None})
        assert response.status_code == 200
        assert response.json()["assignee"] is None

    def test_changing_status_moves_task_to_end_of_new_column(self, client: TestClient) -> None:
        create(client, title="Already in progress", status="in_progress")
        task = create(client, title="Moving over", status="todo")

        response = client.patch(f"/tasks/{task['id']}", json={"status": "in_progress"})
        assert response.status_code == 200
        moved = response.json()
        assert moved["status"] == "in_progress"
        assert moved["order"] == 1  # appended after the existing in_progress task

    def test_empty_body_is_rejected(self, client: TestClient) -> None:
        task = create(client, title="Original")
        response = client.patch(f"/tasks/{task['id']}", json={})
        assert response.status_code == 400

    def test_unknown_task_is_404(self, client: TestClient) -> None:
        response = client.patch("/tasks/does-not-exist", json={"title": "New"})
        assert response.status_code == 404
        assert response.json() == {"message": "Task not found"}

    def test_blank_title_is_rejected(self, client: TestClient) -> None:
        task = create(client, title="Original")
        response = client.patch(f"/tasks/{task['id']}", json={"title": "  "})
        assert response.status_code == 400


class TestDeleteTask:
    def test_deletes_the_task(self, client: TestClient) -> None:
        task = create(client, title="Temporary")
        response = client.delete(f"/tasks/{task['id']}")
        assert response.status_code == 204

        remaining = client.get("/tasks").json()
        assert remaining == []

    def test_unknown_task_is_404(self, client: TestClient) -> None:
        response = client.delete("/tasks/does-not-exist")
        assert response.status_code == 404
        assert response.json() == {"message": "Task not found"}


class TestMoveTask:
    def test_move_between_columns_renumbers_destination(self, client: TestClient) -> None:
        a = create(client, title="A", status="in_progress")
        b = create(client, title="B", status="in_progress")
        moving = create(client, title="Moving", status="todo")

        response = client.post(
            f"/tasks/{moving['id']}/move",
            json={"status": "in_progress", "index": 1},
        )
        assert response.status_code == 200
        by_id = {t["id"]: t for t in response.json()}

        assert by_id[moving["id"]]["status"] == "in_progress"
        # Inserted at index 1: A stays first, moving second, B pushed to third.
        assert by_id[a["id"]]["order"] == 0
        assert by_id[moving["id"]]["order"] == 1
        assert by_id[b["id"]]["order"] == 2

    def test_reorder_within_same_column(self, client: TestClient) -> None:
        first = create(client, title="First", status="todo")
        second = create(client, title="Second", status="todo")
        third = create(client, title="Third", status="todo")

        response = client.post(
            f"/tasks/{third['id']}/move",
            json={"status": "todo", "index": 0},
        )
        assert response.status_code == 200
        by_id = {t["id"]: t for t in response.json()}
        assert by_id[third["id"]]["order"] == 0
        assert by_id[first["id"]]["order"] == 1
        assert by_id[second["id"]]["order"] == 2

    def test_source_column_keeps_its_remaining_order_values(self, client: TestClient) -> None:
        # Mirrors moveTask() in use-board.ts: only the destination column
        # is renumbered, so a gap can persist in the source column.
        first = create(client, title="First", status="todo")
        second = create(client, title="Second", status="todo")

        response = client.post(
            f"/tasks/{first['id']}/move",
            json={"status": "done", "index": 0},
        )
        assert response.status_code == 200
        by_id = {t["id"]: t for t in response.json()}
        assert by_id[second["id"]]["status"] == "todo"
        assert by_id[second["id"]]["order"] == 1  # unchanged, not compacted to 0

    def test_index_beyond_column_length_is_clamped_to_the_end(self, client: TestClient) -> None:
        existing = create(client, title="Existing", status="todo")
        moving = create(client, title="Moving", status="in_progress")

        response = client.post(
            f"/tasks/{moving['id']}/move",
            json={"status": "todo", "index": 999},
        )
        assert response.status_code == 200
        by_id = {t["id"]: t for t in response.json()}
        assert by_id[existing["id"]]["order"] == 0
        assert by_id[moving["id"]]["order"] == 1

    def test_unknown_task_is_404(self, client: TestClient) -> None:
        response = client.post(
            "/tasks/does-not-exist/move",
            json={"status": "todo", "index": 0},
        )
        assert response.status_code == 404

    def test_negative_index_is_rejected(self, client: TestClient) -> None:
        task = create(client, title="A")
        response = client.post(
            f"/tasks/{task['id']}/move",
            json={"status": "todo", "index": -1},
        )
        assert response.status_code == 400
