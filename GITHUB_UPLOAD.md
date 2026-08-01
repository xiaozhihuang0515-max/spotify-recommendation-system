# Upload to GitHub

This repository is ready to publish as the **Spotify AI Recommendation Platform**.

## Include in GitHub

- `app/` — FastAPI backend, database models, and recommendation engine
- `frontend/` — React and TypeScript user interface
- `data/spotify_tracks.csv` — Supplied dataset used by the demo
- `db/` — PostgreSQL schema
- `docker-compose.yml`, `backend.Dockerfile`, and `frontend/Dockerfile`
- `README.md`, `PROJECT_GUIDE.md`, and `RESUME_PROJECT.md`
- `requirements.txt`, `.env.example`, and `.gitignore`

## Automatically excluded

`.gitignore` prevents local-only files from being uploaded: Python virtual environments, frontend dependencies, build output, Python caches, macOS metadata, the local SQLite database, and the unrelated `ecommerce-intelligence-platform/` folder.

## Publish commands

Create a new empty repository on GitHub named `spotify-ai-recommendation-platform`. Do not initialize it with a README. Then run these commands in Terminal:

```bash
cd ~/Desktop/spotify-eda-project
git init
git add .
git status
git commit -m "Build Spotify AI recommendation platform"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/spotify-ai-recommendation-platform.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username. Before running `git commit`, inspect the `git status` output and confirm that `.venv/`, `frontend/node_modules/`, `spotify_ai.db`, `__pycache__/`, and `ecommerce-intelligence-platform/` are absent.
