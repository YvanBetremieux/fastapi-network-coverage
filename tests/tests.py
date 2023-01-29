"""Test module"""
import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    """Provide a testclient instance for tests"""
    return TestClient(app)


def test_health(client):
    """Test health entrypoint"""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == "The api is running"
