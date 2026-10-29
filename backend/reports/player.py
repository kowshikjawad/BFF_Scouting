"""A bounded, one-page scouting snapshot of recorded facts."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from backend.models.provenance import data_source

FONT = "ScoutVera"
if FONT not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(TTFont(FONT, str(Path(reportlab.__file__).parent / "fonts/Vera.ttf")))


def report_filename(player_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "-", player_id)[:80] or "player"
    return f"{safe}-scout-report.pdf"


def render_report(player: dict[str, object]) -> bytes:
    synthetic = data_source(str(player["id"])) == "synthetic"
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    ink, green, muted = "#19342b", "#176347", "#61726a"
    pdf.setTitle(f"Scouting report - {player.get('name') or player['id']}")
    pdf.setAuthor("ShonarTalent AI")

    def text(value: object, x: float, y: float, size: float = 10, color: str = ink):
        pdf.setFillColor(colors.HexColor(color))
        pdf.setFont(FONT, size)
        pdf.drawString(x, y, str(value))

    def paragraph(value: object, x: float, y: float, max_width: float, size: float = 10):
        # Truncate hostile/unbounded source strings before layout; two lines per fact maximum.
        content = str(value) if value is not None else "Not recorded"
        limit = 600 if max_width > 350 else 150
        if len(content) > limit:
            content = content[: limit - 3] + "..."
        style = ParagraphStyle(
            "fact",
            fontName=FONT,
            fontSize=size,
            leading=size * 1.4,
            textColor=colors.HexColor(ink),
            alignment=TA_LEFT,
        )
        p = Paragraph(escape(content), style)
        _, ph = p.wrap(max_width, 100)
        p.drawOn(pdf, x, y - ph)

    def rule(y: float):
        pdf.setStrokeColor(colors.HexColor("#dfe6df"))
        pdf.line(42, y, width - 42, y)

    pdf.setFillColor(colors.HexColor(green))
    pdf.rect(0, height - 9, width, 9, fill=1, stroke=0)
    text("SHONARTALENT / SCOUTING INTELLIGENCE", 42, 795, 9, green)
    text("SYNTHETIC DEMO - FICTIONAL DATA" if synthetic else "PLAYER REPORT", 42, 757, 10, muted)
    name = str(player.get("name") or player["id"])
    paragraph(name, 42, 741, width - 84, 23 if len(name) < 38 else 16)
    paragraph(player.get("league_band"), 42, 678, width - 84, 10)
    rule(628)
    text("RECORDED PROFILE", 42, 604, 10, green)
    value = player.get("estimated_value_eur")
    facts = [
        ("Position", player.get("position")),
        ("Age", f"{player['age']} years" if player.get("age") is not None else None),
        ("Preferred foot", player.get("strong_foot")),
        ("Height", f"{player['height_cm']:g} cm" if player.get("height_cm") else None),
        ("Estimated value", f"EUR {value:,.0f}" if value is not None else None),
        ("Contract expiry", player.get("contract_expiry")),
    ]
    for index, (label, value) in enumerate(facts):
        x, y = 42 + (index % 3) * 174, 578 - (index // 3) * 68
        text(label, x, y, 8, muted)
        paragraph(value, x, y - 10, 158, 10)
    rule(450)
    text("RECORDED ELIGIBILITY STATUS", 42, 426, 10, green)
    paragraph(player.get("ancestry_eligibility") or "Not assessed", 42, 412, width - 84, 12)
    paragraph(
        "Fictional demo status, not an eligibility assessment of a real person."
        if synthetic
        else "Recorded screening only. Confirm nationality, supporting documents and any "
        "association switch with the relevant federation.",
        42,
        383,
        width - 84,
        9,
    )
    rule(341)
    text("TACTICAL METRICS", 42, 317, 10, green)
    metrics = [
        ("Goals /90", "goals_per_90"),
        ("Key passes /90", "key_passes_per_90"),
        ("Prog. carries /90", "progressive_carries_per_90"),
        ("Tackles won /90", "tackles_won_per_90"),
        ("Aerial duels %", "aerial_duel_pct"),
    ]
    for i, (label, key) in enumerate(metrics):
        x = 42 + i * 103
        text(label, x, 290, 7.5, muted)
        value = player.get(key)
        text(f"{value:.2f}" if value is not None else "Not recorded", x, 268, 9)
    paragraph(
        "All tactical values are computer-generated demo figures. They demonstrate the "
        "comparison tools and are not observations or predictions of real performance."
        if synthetic
        else "Metrics are recorded values, not estimates. Missing coverage does not indicate "
        "poor performance. Similarity depends on the available comparison pool.",
        42,
        239,
        width - 84,
        9,
    )
    rule(185)
    text("DATA NOTE", 42, 163, 9, green)
    paragraph(
        "This entire profile is synthetic: name, club, age, contract, valuation and metrics. "
        "Generated deterministically for demonstrations; do not use for recruitment decisions."
        if synthetic
        else "Source coverage varies by league. Profiles may be incomplete or outdated; verify "
        "club, age and contract details before recruitment decisions. This report is a "
        "snapshot of the local scouting database.",
        42,
        149,
        width - 84,
        9,
    )
    rule(73)
    text(f"Generated {datetime.now(timezone.utc):%d %b %Y} (UTC)", 42, 52, 8, muted)
    text("ShonarTalent AI  /  1 of 1", width - 200, 52, 8, muted)
    pdf.showPage()
    pdf.save()
    return output.getvalue()
