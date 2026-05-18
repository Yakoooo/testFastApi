from datetime import UTC, datetime, timedelta


def test_tasks_require_authentication(client):
    response = client.get("/api/v1/tasks")

    assert response.status_code == 401


def test_create_list_get_update_and_delete_task(
    client,
    auth_headers,
    create_project,
):
    project = create_project()

    create_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Design API",
            "description": "Draft task endpoints",
            "status": "todo",
            "project_id": project["id"],
            "priority": "high",
            "assignee_id": None,
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 200
    task = create_response.json()
    assert task["title"] == "Design API"
    assert task["project_id"] == project["id"]
    assert task["creator_id"] == project["owner_id"]

    list_response = client.get("/api/v1/tasks", headers=auth_headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [task["id"]]

    get_response = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == task["id"]

    update_response = client.put(
        f"/api/v1/tasks/{task['id']}",
        json={"title": "Design API v2", "status": "in_progress"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Design API v2"
    assert updated_task["status"] == "in_progress"

    delete_response = client.delete(f"/api/v1/tasks/{task['id']}", headers=auth_headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers)
    assert missing_response.status_code == 404


def test_task_assignee_must_be_project_member(
    client,
    auth_headers,
    create_project,
    register_user,
):
    project = create_project()
    bob = register_user(
        username="bob",
        email="bob@example.com",
        password="secret123",
    )

    rejected_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Assign task",
            "project_id": project["id"],
            "assignee_id": bob["id"],
        },
        headers=auth_headers,
    )
    assert rejected_response.status_code == 403

    client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_list": [bob["id"]]},
        headers=auth_headers,
    )

    accepted_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Assign task",
            "project_id": project["id"],
            "assignee_id": bob["id"],
        },
        headers=auth_headers,
    )
    assert accepted_response.status_code == 200
    assert accepted_response.json()["assignee_id"] == bob["id"]


def test_list_tasks_supports_business_filters_sorting_and_pagination(
    client,
    auth_headers,
    create_project,
    register_user,
):
    project = create_project()
    bob = register_user(
        username="bob",
        email="bob@example.com",
        password="secret123",
    )
    client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_list": [bob["id"]]},
        headers=auth_headers,
    )

    now = datetime.now(UTC)
    task_payloads = [
        {
            "title": "Backlog",
            "project_id": project["id"],
            "status": "todo",
            "priority": "low",
            "due_date": (now + timedelta(days=3)).isoformat(),
        },
        {
            "title": "Build",
            "project_id": project["id"],
            "status": "in_progress",
            "priority": "high",
            "assignee_id": bob["id"],
            "due_date": (now + timedelta(days=1)).isoformat(),
        },
        {
            "title": "Review",
            "project_id": project["id"],
            "status": "review",
            "priority": "urgent",
            "due_date": (now + timedelta(days=2)).isoformat(),
        },
    ]
    for payload in task_payloads:
        response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
        assert response.status_code == 200

    filtered_response = client.get(
        "/api/v1/tasks",
        params={
            "project_id": project["id"],
            "status": "in_progress",
            "priority": "high",
            "assignee_id": bob["id"],
            "creator_id": project["owner_id"],
        },
        headers=auth_headers,
    )
    assert filtered_response.status_code == 200
    assert [task["title"] for task in filtered_response.json()] == ["Build"]

    sorted_response = client.get(
        "/api/v1/tasks",
        params={
            "project_id": project["id"],
            "sort_by": "due_date",
            "sort_order": "asc",
            "skip": 1,
            "limit": 2,
        },
        headers=auth_headers,
    )
    assert sorted_response.status_code == 200
    assert [task["title"] for task in sorted_response.json()] == ["Review", "Backlog"]


def test_task_status_transitions_comments_and_activity_log(
    client,
    auth_headers,
    create_task,
):
    task = create_task()

    invalid_response = client.put(
        f"/api/v1/tasks/{task['id']}",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert invalid_response.status_code == 400

    update_response = client.put(
        f"/api/v1/tasks/{task['id']}",
        json={"title": "Write tests v2", "status": "in_progress"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"

    comment_response = client.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={"content": "接口行为确认完成"},
        headers=auth_headers,
    )
    assert comment_response.status_code == 201
    assert comment_response.json()["content"] == "接口行为确认完成"

    comments_response = client.get(
        f"/api/v1/tasks/{task['id']}/comments",
        headers=auth_headers,
    )
    assert comments_response.status_code == 200
    assert [comment["content"] for comment in comments_response.json()] == ["接口行为确认完成"]

    activities_response = client.get(
        f"/api/v1/tasks/{task['id']}/activities",
        headers=auth_headers,
    )
    assert activities_response.status_code == 200
    activities = activities_response.json()
    actions = [activity["action"] for activity in activities]
    assert "created" in actions
    assert "status_changed" in actions
    assert "updated" in actions
    assert "commented" in actions

    status_activity = next(activity for activity in activities if activity["action"] == "status_changed")
    assert status_activity["field"] == "status"
    assert status_activity["old_value"] == "todo"
    assert status_activity["new_value"] == "in_progress"
