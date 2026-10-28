def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_dialects(client):
    response = client.get("/v1/dialects")
    assert response.status_code == 200
    assert "postgres" in response.json()["dialects"]

