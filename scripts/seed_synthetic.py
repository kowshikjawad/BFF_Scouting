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
# Radar metrics, in TACTICAL_METRICS order:
# goals/90, assists/90, key passes/90, progressive carries/90, dribbles/90,
# tackles won/90, interceptions/90, aerial-duel percentage.
PROFILES = {
    "CM": (0.16, 0.14, 1.7, 3.0, 1.4, 1.8, 1.5, 48),
    "DM": (0.07, 0.08, 0.9, 1.8, 0.7, 3.0, 2.1, 59),
    "AM": (0.29, 0.26, 2.7, 4.1, 2.3, 0.8, 0.7, 35),
    "ST": (0.59, 0.21, 0.9, 2.1, 1.8, 0.5, 0.4, 55),
    "LW": (0.35, 0.28, 2.0, 5.2, 3.1, 0.9, 0.6, 32),
    "RW": (0.36, 0.27, 1.9, 5.0, 3.0, 0.9, 0.6, 34),
    "CB": (0.05, 0.03, 0.4, 0.8, 0.3, 2.5, 1.8, 73),
    "LB": (0.07, 0.10, 1.2, 3.5, 1.5, 2.6, 1.6, 49),
    "RB": (0.08, 0.11, 1.1, 3.3, 1.5, 2.7, 1.6, 50),
    "GK": (0.0, 0.01, 0.12, 0.18, 0.05, 0.12, 0.1, 66),
}
# Reference stats, in REFERENCE_METRICS order:
# shots/90, shot accuracy %, pass completion %, clearances/90.
REFERENCE_PROFILES = {
    "CM": (1.3, 34, 86, 1.1),
    "DM": (0.6, 32, 88, 2.4),
    "AM": (1.9, 37, 83, 0.5),
    "ST": (3.1, 42, 76, 0.3),
    "LW": (2.4, 39, 80, 0.4),
    "RW": (2.3, 39, 80, 0.4),
    "CB": (0.3, 30, 90, 5.8),
    "LB": (0.9, 31, 84, 2.9),
    "RB": (0.9, 31, 84, 2.9),
    "GK": (0.0, 0, 68, 0.6),
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
    "assists_per_90",
    "key_passes_per_90",
    "progressive_carries_per_90",
    "dribbles_per_90",
    "tackles_won_per_90",
    "interceptions_per_90",
    "aerial_duel_pct",
)
_AERIAL_INDEX = METRICS.index("aerial_duel_pct")
_CREATIVE_INDICES = {
    METRICS.index("assists_per_90"),
    METRICS.index("key_passes_per_90"),
    METRICS.index("progressive_carries_per_90"),
    METRICS.index("dribbles_per_90"),
}


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
                    if metric_index == _AERIAL_INDEX:
                        value = baseline + rng.uniform(-13, 13)
                        values.append(round(min(95, max(5, value)), 2))
                        continue
                    multiplier = creativity if metric_index in _CREATIVE_INDICES else 1
                    value = baseline * quality * multiplier * rng.uniform(0.85, 1.15)
                    values.append(round(max(0, value), 2))

                ref_baselines = REFERENCE_PROFILES[position]
                shots, shot_acc_base, pass_comp_base, clearances_base = ref_baselines
                shots_value = round(shots * quality * rng.uniform(0.85, 1.15), 2)
                shot_accuracy = round(
                    min(100, max(0, shot_acc_base + rng.uniform(-6, 6) + (quality - 1) * 8)), 1
                )
                pass_completion = round(min(100, max(0, pass_comp_base + rng.uniform(-5, 5))), 1)
                clearances_value = round(clearances_base * quality * rng.uniform(0.85, 1.15), 2)
                appearances = rng.randint(12, 34)
                minutes_played = round(
                    appearances * min(90, rng.uniform(50, 88) * min(quality, 1.25))
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
                    "shots_per_90": shots_value,
                    "shot_accuracy_pct": shot_accuracy,
                    "pass_completion_pct": pass_completion,
                    "clearances_per_90": clearances_value,
                    "minutes_played": minutes_played,
                    "appearances": appearances,
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
