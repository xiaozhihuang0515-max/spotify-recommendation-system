from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/api",
    tags=["Recommendation"]
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
# 3. Route: recommend
# =========================
@router.post("/recommend", response_model=RecommendationResponse)
def recommend_songs(request: RecommendationRequest):

    # TODO: replace with real ML / embedding model
    mock_recommendations = [
        SongRecommendation(track_id="track_001", score=0.96),
        SongRecommendation(track_id="track_002", score=0.91),
        SongRecommendation(track_id="track_003", score=0.87),
    ]

    return RecommendationResponse(
        user_id=request.user_id,
        recommendations=mock_recommendations
    )


# =========================
# 4. Health check route (optional)
# =========================
@router.get("/health")
def health():
    return {"status": "ok", "service": "recommendation"}
