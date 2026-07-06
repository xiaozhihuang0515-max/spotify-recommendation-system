from fastapi import FastAPI
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Spotify Recommender API",
    description="A simple music recommendation system",
    version="1.0.0"
)

# =========================
# 1. Request schema
# =========================
class SongFeatures(BaseModel):
    danceability: float
    energy: float
    valence: float
    tempo: float
    acousticness: float
    instrumentalness: float

class RecommendationRequest(BaseModel):
    user_id: str
    liked_songs: List[SongFeatures]


# =========================
# 2. Response schema
# =========================
class SongRecommendation(BaseModel):
    track_id: str
    score: float


class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[SongRecommendation]


# =========================
# 3. Health check
# =========================
@app.get("/")
def home():
    return {"message": "Spotify Recommender is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# =========================
# 4. Recommendation endpoint
# =========================
@app.post("/recommend", response_model=RecommendationResponse)
def recommend_songs(request: RecommendationRequest):
    """
    Dummy recommender for now.
    Later we will replace this with:
    - embedding model
    - similarity search
    - or ML model inference
    """

    # TODO: replace with real model logic
    mock_recommendations = [
        SongRecommendation(track_id="track_001", score=0.95),
        SongRecommendation(track_id="track_002", score=0.89),
        SongRecommendation(track_id="track_003", score=0.85),
    ]

    return RecommendationResponse(
        user_id=request.user_id,
        recommendations=mock_recommendations
    )
