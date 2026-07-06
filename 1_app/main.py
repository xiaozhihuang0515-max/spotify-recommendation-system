from fastapi import FastAPI
from app.routes import recommend

app = FastAPI(
    title="Spotify Recommender API",
    version="1.0.0"
)

app.include_router(recommend.router)


@app.get("/")
def root():
    return {"message": "Spotify Recommender is running 🚀"}
