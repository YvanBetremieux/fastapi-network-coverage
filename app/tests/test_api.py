"""Test module"""
import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    """Provide a testclient instance for tests"""
    return TestClient(app)


def test_health(client):
    """
    Test health entrypoint
    :param client: TestClient to test api
    :return: Assertions ok
    """

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == "The api is running"


def test_get_coverage_network(client):
    """
    Test get_coverage_network entrypoint
    :param client: TestClient to test api
    :return: Assertions ok
    """

    response = client.get("/network/coverage", params={"q": "rue marcel magard, 63170"})

    assert response.status_code == 200
    assert response.json() == {
        "Orange": {"2G": True, "3G": True, "4G": True},
        "S.F.R.": {"2G": True, "3G": True, "4G": True},
        "Lliad/FREE Mobile": {"2G": False, "3G": True, "4G": True},
        "Bouygues Telecom": {"2G": True, "3G": True, "4G": True},
    }
