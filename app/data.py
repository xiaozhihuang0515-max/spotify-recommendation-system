from __future__ import annotations

import csv
import math
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "spotify_tracks.csv"
FEATURES = (
    "danceability",
    "energy",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
)
NUMERIC_COLUMNS = FEATURES + ("popularity", "duration_ms", "loudness")


def _number(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


@lru_cache(maxsize=1)
def tracks() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8-sig", newline="") as source:
        rows = []
        for raw in csv.DictReader(source):
            if not raw.get("track_id") or not raw.get("track_genre"):
                continue
            row = {key: value for key, value in raw.items() if key}
            for column in NUMERIC_COLUMNS:
                row[column] = _number(row.get(column))
            row["explicit"] = str(row.get("explicit", "")).lower() == "true"
            rows.append(row)
    return rows


@lru_cache(maxsize=1)
def feature_stats() -> dict[str, tuple[float, float]]:
    result = {}
    for feature in FEATURES:
        values = [float(row[feature]) for row in tracks()]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        result[feature] = (mean, math.sqrt(variance) or 1.0)
    return result


def embedding(row: dict) -> list[float]:
    return [
        (float(row[feature]) - feature_stats()[feature][0])
        / feature_stats()[feature][1]
        for feature in FEATURES
    ]


def cosine_distance(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return 1 - dot / (left_norm * right_norm) if left_norm and right_norm else 1.0

