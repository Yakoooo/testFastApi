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
