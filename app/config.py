import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spotify_ai.db")
