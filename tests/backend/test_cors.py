"""CORS is enabled for the local Vite dev server origin."""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


def test_allows_the_vite_dev_server_origin():
    with TestClient(app) as client:
        resp = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
