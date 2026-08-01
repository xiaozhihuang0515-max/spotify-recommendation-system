from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import FeedbackAction, User
from app.schemas import FeedbackCreate, FeedbackResponse, Recommendation, UserProfile
from app.services.recommendation_engine import recommendation_engine
from app.services.user_service import get_or_create_demo_user, record_feedback
from visualization.charts import genre_overview, popularity_histogram, scatter_sample
from app.data import tracks

ROOT = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Spotify AI Recommendation Platform",
    description="Content-based music recommendations, user analytics, and feedback tracking.",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, int | str]:
    return {"status": "ok", "tracks": len(tracks())}


@app.get("/users/{user_id}/profile", response_model=UserProfile)
def user_profile(user_id: int, db: Session = Depends(get_db)) -> UserProfile:
    user = get_or_create_demo_user(db, user_id)
    return recommendation_engine.build_profile(user)


@app.get("/recommendations/{user_id}", response_model=list[Recommendation])
def recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[Recommendation]:
    user = get_or_create_demo_user(db, user_id)
    return recommendation_engine.recommend_songs(user, db, top_k=limit)


@app.post("/feedback", response_model=FeedbackResponse, status_code=201)
def feedback(payload: FeedbackCreate, db: Session = Depends(get_db)) -> FeedbackResponse:
    if payload.action not in (FeedbackAction.LIKE, FeedbackAction.DISLIKE):
        raise HTTPException(status_code=422, detail="action must be like or dislike")
    get_or_create_demo_user(db, payload.user_id)
    return record_feedback(db, payload)


@app.get("/users/{user_id}/favorites", response_model=list[Recommendation])
def favorites(user_id: int, db: Session = Depends(get_db)) -> list[Recommendation]:
    user = get_or_create_demo_user(db, user_id)
    return recommendation_engine.favorite_songs(user, db)


@app.get("/analytics/{user_id}")
def analytics(user_id: int, db: Session = Depends(get_db)) -> dict:
    user = get_or_create_demo_user(db, user_id)
    return recommendation_engine.analytics(user, db)


# Data explorer endpoints remain available for the original EDA notebook/dashboard.
@app.get("/api/summary")
def summary() -> dict:
    rows = tracks()
    return recommendation_engine.dataset_summary(rows)


@app.get("/api/visualizations")
def visualizations() -> dict:
    rows = tracks()
    return {
        "genres": genre_overview(rows),
        "popularity": popularity_histogram(rows),
        "scatter": scatter_sample(rows),
    }


@app.get("/api/tracks")
def search_tracks(q: str = Query(default="", max_length=100), limit: int = Query(default=12, ge=1, le=50)) -> list[dict]:
    needle = q.casefold().strip()
    results = [row for row in tracks() if not needle or needle in f"{row['track_name']} {row['artists']}".casefold()]
    return sorted(results, key=lambda row: float(row["popularity"]), reverse=True)[:limit]

