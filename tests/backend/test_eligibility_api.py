"""API-level test for the eligibility endpoint (FR-2.1/2.2).

The engine's rule logic is covered exhaustively in test_eligibility.py --
this just confirms the route is reachable as POST (a browser's fetch()
cannot send a body on GET/HEAD; see openspec scouting-dashboard-ui
design.md decision #5) and maps the engine's result correctly.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


def test_eligibility_is_a_post_route():
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/players/p1/eligibility",
            json={"born_in_territory": True, "born_in_territory_documented": True},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["player_id"] == "p1"
    assert body["status"] == "ELIGIBLE & CLEARED"


def test_eligibility_get_is_no_longer_available():
    with TestClient(app) as client:
        resp = client.get("/api/v1/players/p1/eligibility")
    assert resp.status_code == 405
