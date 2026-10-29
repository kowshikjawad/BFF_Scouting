"""Deterministic, offline fictional scouting records. Never fills facts on real players."""

from __future__ import annotations

import random
from datetime import date

from sqlalchemy.orm import Session

from backend.models.db import init_db, session_scope
from backend.models.player import Player
from backend.models.player_records import upsert_player
from backend.models.provenance import SYNTHETIC_PREFIX

SEED = 20261028
# Goals/90, key passes/90, progressive carries/90, tackles won/90, aerial-duel percentage.
PROFILES = {
    "CM": (0.16, 1.7, 3.0, 1.8, 48),
    "DM": (0.07, 0.9, 1.8, 3.0, 59),
    "AM": (0.29, 2.7, 4.1, 0.8, 35),
    "ST": (0.59, 0.9, 2.1, 0.5, 55),
    "LW": (0.35, 2.0, 5.2, 0.9, 32),
    "RW": (0.36, 1.9, 5.0, 0.9, 34),
    "CB": (0.05, 0.4, 0.8, 2.5, 73),
    "LB": (0.07, 1.2, 3.5, 2.6, 49),
    "RB": (0.08, 1.1, 3.3, 2.7, 50),
    "GK": (0.0, 0.12, 0.18, 0.12, 66),
}
LEAGUES = [
    ("Demo Bangladesh League", ["Padma Athletic", "Meghna United", "Delta Sporting", "Surma FC"]),
    (
        "Demo UK Development League",
        ["Northbridge Rovers", "Cedar Town", "Alder City", "Vale Athletic"],
    ),
    ("Demo European League", ["Harbor Sporting", "Eastbank FC", "Silverwood", "Ridge United"]),
    ("Demo North America League", ["Lakeview SC", "Maple Athletic", "Rivergate FC", "Pine United"]),
]
FIRST_NAMES = [
    "Arian",
    "Rafi",
    "Nabil",
    "Sami",
    "Zayan",
    "Ishan",
    "Adil",
    "Rayhan",
    "Nihan",
    "Tasin",
    "Zahir",
    "Rayan",
    "Faris",
    "Naeem",
    "Rehan",
    "Arif",
]
LAST_NAMES = [
    "Rahman",
    "Hasan",
    "Karim",
    "Ahmed",
    "Islam",
    "Khan",
    "Alam",
    "Hossain",
    "Siddiq",
    "Mahmud",
]
METRICS = (
    "goals_per_90",
    "key_passes_per_90",
    "progressive_carries_per_90",
    "tackles_won_per_90",
    "aerial_duel_pct",
)


def generate_players(seed: int = SEED) -> list[dict]:
    """160 reproducible records, four complete profiles per league/position; no external calls."""
    rng = random.Random(seed)
    records = []
    for league_index, (league, clubs) in enumerate(LEAGUES):
        for position, baselines in PROFILES.items():
            for variant in range(4):
                index = len(records)
                age = rng.randint(18, 34)
                quality = rng.uniform(0.75, 1.3)
                creativity = rng.uniform(0.8, 1.2)
                values = []
                for metric_index, baseline in enumerate(baselines):
                    multiplier = creativity if metric_index in (1, 2) else 1
                    value = baseline * quality * multiplier * rng.uniform(0.85, 1.15)
                    if metric_index == 4:
                        value = baseline + rng.uniform(-13, 13)
                    values.append(
                        round(min(95, max(5, value)) if metric_index == 4 else max(0, value), 2)
                    )
                height_base = 189 if position in ("GK", "CB") else 175
                record = {
                    "id": f"{SYNTHETIC_PREFIX}{index + 1:03d}",
                    "name": f"{FIRST_NAMES[index % 16]} {LAST_NAMES[index // 16]}",
                    "age": age,
                    "position": position,
                    "height_cm": rng.randint(height_base - 6, height_base + 6),
                    "strong_foot": rng.choices(["Right", "Left", "Both"], [6, 3, 1])[0],
                    "league_band": f"{league} -- {clubs[variant]}",
                    "contract_expiry": date(2027 + variant, 6, 30).isoformat(),
                    "estimated_value_eur": round(
                        (quality * 350_000 + league_index * 100_000)
                        * (1.3 if age < 24 else 0.8)
                        / 5000
                    )
                    * 5000,
                    "ancestry_eligibility": [
                        "ELIGIBLE & CLEARED",
                        "DOCUMENTATION REQUIRED",
                        "INELIGIBLE",
                        None,
                    ][variant],
                    **dict(zip(METRICS, values)),
                }
                Player(**record)  # Validate the same shape consumed by the API.
                records.append(record)
    return records


def seed_synthetic(session: Session) -> int:
    records = generate_players()
    for record in records:
        upsert_player(session, record["id"], **{k: v for k, v in record.items() if k != "id"})
    return len(records)


def main():
    init_db()
    with session_scope() as session:
        count = seed_synthetic(session)
    print(f"Loaded {count} fictional synthetic profiles (seed {SEED}); real records unchanged.")


if __name__ == "__main__":
    main()
