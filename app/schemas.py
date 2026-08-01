from datetime import datetime

from pydantic import BaseModel, Field

from app.models import FeedbackAction


class UserProfile(BaseModel):
    user_id: int
    username: str
    favorite_genre: str
    top_artist: str
    listening_pattern: str
    average_energy: float
    genre_breakdown: list[dict[str, float | str]]
    audio_features: dict[str, float]


class Recommendation(BaseModel):
    song_id: str
    title: str
    artist: str
    genre: str
    popularity: int
    similarity: float
    reason: str
    cover_color: str
    added_at: datetime | None = None


class FeedbackCreate(BaseModel):
    user_id: int = Field(gt=0)
    song_id: str
    action: FeedbackAction


class FeedbackResponse(BaseModel):
    interaction_id: int
    action: FeedbackAction
    timestamp: datetime
