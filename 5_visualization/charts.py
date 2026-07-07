from __future__ import annotations

from collections import Counter, defaultdict


def genre_overview(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row["track_genre"])].append(row)
    return [
        {
            "genre": genre,
            "tracks": len(items),
            "avg_popularity": round(
                sum(float(item["popularity"]) for item in items) / len(items), 1
            ),
            "avg_energy": round(
                sum(float(item["energy"]) for item in items) / len(items), 3
            ),
        }
        for genre, items in sorted(grouped.items())
    ]


def popularity_histogram(rows: list[dict], width: int = 10) -> list[dict]:
    bins = Counter(
        min(90, int(float(row["popularity"]) // width) * width) for row in rows
    )
    return [
        {"label": f"{start}–{start + width - 1}", "count": bins[start]}
        for start in range(0, 100, width)
    ]


def scatter_sample(rows: list[dict], limit: int = 600) -> list[dict]:
    step = max(1, len(rows) // limit)
    return [
        {
            "energy": row["energy"],
            "danceability": row["danceability"],
            "popularity": row["popularity"],
            "genre": row["track_genre"],
            "track": row["track_name"],
        }
        for row in rows[::step][:limit]
    ]

