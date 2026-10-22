"""Smoke test: FastAPI app boots and health endpoint responds."""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


def test_health():
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"