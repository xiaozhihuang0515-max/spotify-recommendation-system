# spotify-recommendation-system

A portfolio-ready full-stack music discovery product. It pairs a responsive React dashboard with FastAPI APIs, PostgreSQL persistence, and a content-based recommendation engine trained from Spotify audio features.

## Highlights

- Personalized dashboard with music profile, genre mix, audio-feature radar, and listening analytics.
- Top-K content recommendations using standardized audio features and cosine similarity.
- Like/dislike feedback persists to the database and immediately updates recommendations and favorites.
- Production-shaped service layout: REST API, SQLAlchemy models, PostgreSQL Docker service, and separate frontend build.

## Architecture

```text
React + TypeScript (Nginx)  ->  FastAPI  ->  PostgreSQL
                                     |
                                     ->  NumPy similarity engine + Spotify CSV
```

## Repository layout

```text
app/                 FastAPI routes, ORM models, schemas, services
app/services/        Recommendation and feedback business logic
frontend/            React + TypeScript + Vite dashboard
data/                Supplied Spotify track dataset
db/schema.sql        PostgreSQL schema reference
docker-compose.yml   Full local deployment
```

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/users/{user_id}/profile` | Music profile and feature preferences |
| `GET` | `/recommendations/{user_id}` | Personalized top-K tracks |
| `POST` | `/feedback` | Save `{ user_id, song_id, action }` feedback |
| `GET` | `/users/{user_id}/favorites` | Liked tracks |
| `GET` | `/analytics/{user_id}` | Listening trend and audience segment |
| `GET` | `/docs` | Interactive OpenAPI documentation |

## Run locally

The backend defaults to SQLite so it can be started without PostgreSQL:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal, run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite server proxies API requests to FastAPI at `http://localhost:8000`.

## Docker deployment

```bash
docker compose up --build
```

Open `http://localhost:5173`; FastAPI docs are at `http://localhost:8000/docs`. Docker configures PostgreSQL automatically. For other environments, copy `.env.example` and set `DATABASE_URL`.

## Recommendation algorithm

The engine cleans numeric audio fields, standardizes each feature using the dataset mean and standard deviation, and forms a user preference vector from likes (or a deterministic onboarding seed). It ranks cosine similarity between that preference vector and every candidate song, excludes disliked tracks, then stores displayed recommendation scores in history.

## Future improvements

- Replace simulated onboarding activity with Spotify OAuth and real listening events.
- Add migrations, authentication, background recommendation refreshes, and observability.
- Add hybrid collaborative filtering once interaction volume is sufficient.
