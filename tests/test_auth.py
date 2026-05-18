def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "secret123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert data["is_active"] is True
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_rejects_duplicate_email(client, register_user):
    register_user()

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice2",
            "password": "secret123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["msg"] == "Email already registered"


def test_login_returns_bearer_token(client, register_user):
    register_user(username="alice", password="secret123")

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "alice", "password": "secret123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_rejects_bad_password(client, register_user):
    register_user(username="alice", password="secret123")

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "alice", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["msg"] == "Invalid username or password"
