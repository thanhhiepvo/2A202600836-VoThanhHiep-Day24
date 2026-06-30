# tests/test_api.py
import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "token,path,method,expected_status",
    [
        ("token-bob", "/api/patients/raw", "get", 403),
        ("token-alice", "/api/patients/raw", "get", 200),
        ("token-bob", "/api/patients/anonymized", "get", 200),
        ("token-carol", "/api/metrics/aggregated", "get", 200),
        ("token-bob", "/api/patients/abc123", "delete", 403),
        ("token-alice", "/api/patients/abc123", "delete", 200),
        ("token-dave", "/api/patients/raw", "get", 403),
    ],
)
def test_rbac_endpoints(token, path, method, expected_status):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.request(method, path, headers=headers)
    assert response.status_code == expected_status


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
