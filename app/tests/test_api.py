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
    WARNING, you must have import File before
    :param client: TestClient to test api
    :return: Assertions ok
    """

    response = client.get(
        "/network/coverage", params={"adress": "rue marcel magard, 63170"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "Orange": {"2G": True, "3G": True, "4G": True},
        "S.F.R.": {"2G": True, "3G": True, "4G": True},
        "Lliad/FREE Mobile": {"2G": False, "3G": True, "4G": True},
        "Bouygues Telecom": {"2G": True, "3G": True, "4G": True},
    }


def test_get_city(client):
    """
    Test get_city entrypoint
    WARNING, you must have import File before
    :param client: TestClient to test api
    :return: Assertions ok
    """

    response = client.get("/city", params={"city": "Clermont-Ferrand"})

    assert response.status_code == 200
    assert response.json() == {"name": "Clermont-Ferrand"}


def test_city_endpoints(client):
    """
    Test get_city entrypoint
    WARNING, you must have import File before
    :param client: TestClient to test api
    :return: Assertions ok
    """

    # GET NOK
    with pytest.raises(ValueError):
        response = client.get("/city", params={"city": "Pytest"})
    # DELETE NOK
    with pytest.raises(ValueError):
        response = client.delete("/city", params={"city": "Pytest"})
    # DELETE WRONG PARAM
    response = client.delete("/city", params={"name": "Pytest"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "city"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
    # POST WRONG PARAM
    response = client.post("/add/city", params={"city": "Pytest"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"loc": ["body"], "msg": "field required", "type": "value_error.missing"}
        ]
    }
    # POST OK
    response = client.post("/add/city", json={"name": "Pytest"})
    assert response.status_code == 200
    assert response.json() == {"name": "Pytest"}
    # GET OK
    response = client.get("/city", params={"city": "Pytest"})
    assert response.status_code == 200
    assert response.json() == {"name": "Pytest"}
    # DELETE OK
    response = client.delete("/city", params={"city": "Pytest"})
    assert response.status_code == 200
    assert response.json() == {"name": "Pytest"}
    # GET NOK
    with pytest.raises(ValueError):
        response = client.get("/city", params={"city": "Pytest"})


def test_operator_endpoints(client):
    """
    Test get_operator entrypoint
    WARNING, you must have import File before
    :param client: TestClient to test api
    :return: Assertions ok
    """

    # GET NOK
    with pytest.raises(ValueError):
        response = client.get("/operator", params={"code": 1})
    # DELETE NOK
    with pytest.raises(ValueError):
        response = client.delete("/operator", params={"code": 1})
    # DELETE WRONG PARAM
    response = client.delete("/operator", params={"name": "Pytest"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "code"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
    # POST WRONG PARAM
    response = client.post("/add/operator", params={"operator": "Pytest"})
    assert response.status_code == 422
    assert (
        response.json()
        == {
            "detail": [
                {
                    "loc": ["body"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }
        != {"name": "Pytest"}
    )
    # POST OK
    response = client.post("/add/operator", json={"code": 1, "name": "Pytest"})
    assert response.status_code == 200
    assert response.json() == {"code": 1, "name": "Pytest"}
    # GET OK
    response = client.get("/operator", params={"code": 1})
    assert response.status_code == 200
    assert response.json() == {"code": 1, "name": "Pytest"}
    # DELETE OK
    response = client.delete("/operator", params={"code": 1})
    assert response.status_code == 200
    assert response.json() == {"name": "Pytest"}
    # GET NOK
    with pytest.raises(ValueError):
        response = client.get("/operator", params={"code": 1})
