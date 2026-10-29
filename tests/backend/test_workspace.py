"""Regression contracts for the completed scouting workflows."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from backend.app.main import create_app
from backend.models.db import get_session
from backend.models.player_records import upsert_player
from backend.reports.player import render_report, report_filename
from tests.backend import test_players_api


@pytest.fixture()
def client():
    yield from test_players_api.client.__wrapped__()


def test_metric_contract_preserves_values_and_nulls(client):
    player = client.get("/api/v1/players/old-st").json()
    assert player["goals_per_90"] == 0.5
    assert player["aerial_duel_pct"] == 55
    unknown = client.get("/api/v1/players/young-lb").json()
    assert unknown["goals_per_90"] is None


def test_partial_player_records_are_readable(client):
    session = next(client.app.dependency_overrides[get_session]())
    upsert_player(session, "partial", goals_per_90=0.25)
    session.commit()
    session.close()
    data = client.get("/api/v1/players/partial").json()
    assert data["name"] is None
    assert data["goals_per_90"] == 0.25


def test_name_search_is_case_insensitive_literal_and_combinable(client):
    assert [p["id"] for p in client.get("/api/v1/players?q=STRIKER&max_age=30").json()] == [
        "similar-st"
    ]
    assert client.get("/api/v1/players?q=%25").json() == []


def test_position_matches_full_name_and_secondary_role(client):
    session = next(client.app.dependency_overrides[get_session]())
    upsert_player(session, "multi", position="CM / DM", name="Multi")
    upsert_player(session, "full", position="Defensive Midfielder", name="Full")
    session.commit()
    session.close()
    assert {p["id"] for p in client.get("/api/v1/players?position=DM").json()} == {"multi", "full"}


def test_sorting_and_unassessed_filter(client):
    assert [p["id"] for p in client.get("/api/v1/players?sort=age_asc").json()] == [
        "young-lb",
        "similar-st",
        "old-st",
    ]
    assert {
        p["id"] for p in client.get("/api/v1/players?eligibility_status=NOT_ASSESSED").json()
    } == {"old-st", "similar-st"}


@pytest.mark.parametrize(
    "query", ["max_age=-1", "max_value_eur=-5", "max_value_eur=inf", "sort=invalid"]
)
def test_search_rejects_invalid_filters(client, query):
    assert client.get(f"/api/v1/players?{query}").status_code == 422


@pytest.mark.parametrize("top_k", [0, -1, 51])
def test_similarity_bounds(client, top_k):
    assert client.get(f"/api/v1/players/old-st/similar?top_k={top_k}").status_code == 422


def test_pdf_is_a_real_single_page_report(client):
    response = client.get("/api/v1/players/old-st/report.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    reader = PdfReader(BytesIO(response.content))
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert "Veteran Striker" in text and "0.50" in text and "Not recorded" in text
    assert client.get("/api/v1/players/unknown/report.pdf").status_code == 404


def test_report_escapes_source_markup_and_sanitizes_filename():
    report = render_report({"id": 'unsafe"\r\n', "name": "<Scout & Player>", "position": "DM"})
    assert "<Scout & Player>" in PdfReader(BytesIO(report)).pages[0].extract_text()
    assert report_filename('unsafe"\r\n') == "unsafe----scout-report.pdf"


def test_eligibility_rejects_inconsistent_and_negative_residency(client):
    for facts in [
        {"residency_years": -1},
        {"residency_years": 2.5},
        {"residency_years": 2, "residency_years_after_18": 3},
    ]:
        assert client.post("/api/v1/players/test/eligibility", json=facts).status_code == 422


def test_youth_representation_does_not_imply_automatic_clearance(client):
    data = client.post(
        "/api/v1/players/test/eligibility",
        json={
            "born_in_territory": True,
            "born_in_territory_documented": True,
            "has_youth_caps_other_association": True,
        },
    ).json()
    assert data["status"] == "DOCUMENTATION REQUIRED"
    assert data["review_required"] is True
    assert any("association" in reason for reason in data["reasons"])


def test_spa_routes_preserve_api_and_asset_404s(tmp_path):
    (tmp_path / "index.html").write_text("<html>scouting app</html>")
    with TestClient(create_app(tmp_path)) as client:
        assert client.get("/players/test").text == "<html>scouting app</html>"
        assert client.get("/api/v1/missing").status_code == 404
        assert client.get("/missing.js").status_code == 404
        assert client.get("/licenses/missing.txt").status_code == 404
