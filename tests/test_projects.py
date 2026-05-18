def test_projects_require_authentication(client):
    response = client.get("/api/v1/projects/")

    assert response.status_code == 401


def test_create_list_and_get_project(client, auth_headers):
    create_response = client.post(
        "/api/v1/projects/",
        json={"name": "Roadmap", "description": "Q2 execution"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    project = create_response.json()
    assert project["name"] == "Roadmap"
    assert project["description"] == "Q2 execution"
    assert project["task_count"] == 0

    list_response = client.get("/api/v1/projects/", headers=auth_headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [project["id"]]

    get_response = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == project["id"]


def test_project_owner_can_add_and_list_members(
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

    add_response = client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_list": [bob["id"]]},
        headers=auth_headers,
    )
    assert add_response.status_code == 201
    assert add_response.json() == {
        "added_user_ids": [bob["id"]],
        "skipped_user_ids": [],
    }

    duplicate_response = client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_list": [bob["id"]]},
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 201
    assert duplicate_response.json() == {
        "added_user_ids": [],
        "skipped_user_ids": [bob["id"]],
    }

    members_response = client.get(
        f"/api/v1/projects/{project['id']}/members",
        headers=auth_headers,
    )
    assert members_response.status_code == 200
    usernames = {member["username"] for member in members_response.json()}
    assert usernames == {"alice", "bob"}
