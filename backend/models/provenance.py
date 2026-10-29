"""Reserved provenance namespace: generated records cannot impersonate real source data."""

from typing import Literal

SYNTHETIC_PREFIX = "synthetic-v1-"
Dataset = Literal["real", "synthetic"]


def data_source(player_id: str) -> Dataset:
    return "synthetic" if player_id.startswith(SYNTHETIC_PREFIX) else "real"
