from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeedbackAction(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    interaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    song_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[FeedbackAction] = mapped_column(SqlEnum(FeedbackAction))
    play_count: Mapped[int] = mapped_column(Integer, default=0)
    liked: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    song_id: Mapped[str] = mapped_column(String(64), index=True)
    recommendation_score: Mapped[float] = mapped_column(Float)
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
