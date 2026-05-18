def test_health_status(client):
    response = client.get("/api/v1/health/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
