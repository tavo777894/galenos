"""
Health check tests for DB connectivity.
"""
import app.main as main_module
from tests.conftest import client


def test_healthcheck_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_healthcheck_degraded_on_db_failure(monkeypatch):
    def _raise():
        raise Exception("db down")

    monkeypatch.setattr(main_module, "SessionLocal", _raise)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["db"] == "down"
