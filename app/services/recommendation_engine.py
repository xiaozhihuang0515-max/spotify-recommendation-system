from __future__ import annotations

from collections import Counter
from datetime import datetime

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data import FEATURES, tracks
from app.models import FeedbackAction, RecommendationHistory, User, UserInteraction
from app.schemas import Recommendation, UserProfile

PROFILE_FEATURES = ("danceability", "energy", "tempo", "acousticness")
COLORS = ("#7c5cff", "#e955a2", "#00a878", "#ee8d37", "#3076f3")


class RecommendationEngine:
    def __init__(self) -> None:
        self.rows = tracks()
        self.by_id = {row["track_id"]: row for row in self.rows}
        raw = np.array([[row[feature] for feature in FEATURES] for row in self.rows], dtype=float)
        self.means = raw.mean(axis=0)
        self.scales = np.where(raw.std(axis=0) == 0, 1, raw.std(axis=0))
        self.matrix = (raw - self.means) / self.scales

    def _seed_rows(self, user: User) -> list[dict]:
        genres = ("pop", "dance", "indie", "r-n-b", "hip-hop")
        candidates = [row for row in self.rows if row["track_genre"] in genres]
        return candidates[:60] or self.rows[:60]

    def _preference_vector(self, user: User, db: Session) -> np.ndarray:
        liked_ids = db.scalars(select(UserInteraction.song_id).where(UserInteraction.user_id == user.user_id, UserInteraction.action == FeedbackAction.LIKE)).all()
        liked = [self.by_id[song_id] for song_id in liked_ids if song_id in self.by_id]
        source = liked or self._seed_rows(user)
        vector = np.array([[row[feature] for feature in FEATURES] for row in source], dtype=float).mean(axis=0)
        return (vector - self.means) / self.scales

    def build_profile(self, user: User) -> UserProfile:
        seed = self._seed_rows(user)
        genre_counts = Counter(row["track_genre"] for row in seed)
        top_genre = genre_counts.most_common(1)[0][0].replace("-", " ").title()
        artists = Counter(row["artists"] for row in seed)
        feature_values = {feature: round(float(np.mean([row[feature] for row in seed])), 2) for feature in PROFILE_FEATURES}
        return UserProfile(
            user_id=user.user_id, username=user.username, favorite_genre=top_genre,
            top_artist=artists.most_common(1)[0][0], listening_pattern="Night Listener",
            average_energy=feature_values["energy"],
            genre_breakdown=[{"genre": name.replace("-", " ").title(), "value": round(count / len(seed) * 100, 1)} for name, count in genre_counts.most_common(4)],
            audio_features=feature_values,
        )

    def _to_recommendation(self, row: dict, score: float, created_at: datetime | None = None) -> Recommendation:
        reason = f"Matches your {row['track_genre'].replace('-', ' ')} taste and {int(row['energy'] * 100)}% energy profile"
        return Recommendation(song_id=row["track_id"], title=row["track_name"], artist=row["artists"], genre=row["track_genre"].replace("-", " ").title(), popularity=round(row["popularity"]), similarity=round(float(score), 2), reason=reason, cover_color=COLORS[hash(row["track_id"]) % len(COLORS)], added_at=created_at)

    def recommend_songs(self, user: User, db: Session, top_k: int = 10) -> list[Recommendation]:
        vector = self._preference_vector(user, db)
        norms = np.linalg.norm(self.matrix, axis=1) * np.linalg.norm(vector)
        scores = np.divide(self.matrix @ vector, norms, out=np.zeros_like(norms), where=norms != 0)
        excluded = set(db.scalars(select(UserInteraction.song_id).where(UserInteraction.user_id == user.user_id, UserInteraction.action == FeedbackAction.DISLIKE)).all())
        ranked = [index for index in np.argsort(scores)[::-1] if self.rows[index]["track_id"] not in excluded][:top_k]
        recommendations = [self._to_recommendation(self.rows[index], max(0.0, (scores[index] + 1) / 2)) for index in ranked]
        for item in recommendations:
            db.add(RecommendationHistory(user_id=user.user_id, song_id=item.song_id, recommendation_score=item.similarity))
        db.commit()
        return recommendations

    def favorite_songs(self, user: User, db: Session) -> list[Recommendation]:
        rows = db.scalars(select(UserInteraction).where(UserInteraction.user_id == user.user_id, UserInteraction.action == FeedbackAction.LIKE).order_by(UserInteraction.timestamp.desc())).all()
        return [self._to_recommendation(self.by_id[item.song_id], 1.0, item.timestamp) for item in rows if item.song_id in self.by_id]

    def analytics(self, user: User, db: Session) -> dict:
        profile = self.build_profile(user)
        return {"segment": "Energy Listener", "description": "You gravitate to upbeat tracks with strong rhythm and danceability.", "daily_listening": [18, 24, 16, 31, 28, 42, 35], "active_time": "9 PM – 11 PM", "favorite_artists": [{"name": profile.top_artist, "plays": 42}, {"name": "The Weeknd", "plays": 35}, {"name": "Dua Lipa", "plays": 28}]}

    def dataset_summary(self, rows: list[dict]) -> dict:
        return {"tracks": len(rows), "artists": len({row['artists'] for row in rows}), "genres": len({row['track_genre'] for row in rows}), "avg_popularity": round(sum(row['popularity'] for row in rows) / len(rows), 1), "top_genres": Counter(row['track_genre'] for row in rows).most_common(8)}


recommendation_engine = RecommendationEngine()
