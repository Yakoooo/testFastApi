import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.deps import get_db
from app.main import app
from app.models import Project, ProjectMember, Task, User
from app.core.config import settings


SQLALCHEMY_DATABASE_URL = settings.test_database_url
assert SQLALCHEMY_DATABASE_URL, "Set test_database_url before running tests."

test_database = make_url(SQLALCHEMY_DATABASE_URL)
engine_kwargs = {}
if test_database.drivername.startswith("sqlite"):
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def register_user(client):
    def _register_user(
        username: str = "alice",
        email: str = "alice@example.com",
        password: str = "secret123",
    ):
        response = client.post(
            "/api/v1/auth/register",
            json={"username": username, "email": email, "password": password},
        )
        assert response.status_code == 201
        return response.json()

    return _register_user


@pytest.fixture()
def auth_headers(client, register_user):
    register_user()
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "alice", "password": "secret123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def create_project(client, auth_headers):
    def _create_project(name: str = "API Upgrade", description: str | None = "Ship v1"):
        response = client.post(
            "/api/v1/projects/",
            json={"name": name, "description": description},
            headers=auth_headers,
        )
        assert response.status_code == 201
        return response.json()

    return _create_project


@pytest.fixture()
def create_task(client, auth_headers, create_project):
    def _create_task(
        title: str = "Write tests",
        project_id: int | None = None,
        assignee_id: int | None = None,
        status: str = "todo",
        priority: str = "medium",
    ):
        project = create_project() if project_id is None else {"id": project_id}
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": title,
                "description": "Cover the happy path",
                "status": status,
                "project_id": project["id"],
                "priority": priority,
                "assignee_id": assignee_id,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        return response.json()

    return _create_task
