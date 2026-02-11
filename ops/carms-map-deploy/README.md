# CaRMS map/API deploy helpers

Templates to run the CaRMS FastAPI + map service (from `bellonaut/Junior-Data-Scientist`) on a container host instead of Vercel/GitHub Pages.

## Contents
- `Dockerfile` – builds the FastAPI/Dagster app, runs migrations, then starts Uvicorn.
- `fly.toml` – Fly.io app template (expects a separate Fly Postgres instance).
- `render.yaml` – Render blueprint (provisions managed Postgres + web service).

## How to use
1) Clone the CaRMS backend repo (or keep it checked out alongside this site):
   ```
   git clone https://github.com/bellonaut/Junior-Data-Scientist.git carms-backend
   cd carms-backend
   ```
2) Copy the files from `ops/carms-map-deploy/` into the backend repo root (same level as `pyproject.toml`).
3) Set env vars (at minimum): `DATABASE_URL` (Postgres), optionally `API_KEY`, `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SEC`, `APP_MODULE` (if your FastAPI entrypoint differs from the default).

### Fly.io (recommended for quick container + managed Postgres)
```
flyctl postgres create --name carms-pg --region yul --vm-size shared-cpu-1x --volume-size 10
flyctl launch --copy-config --no-deploy --name carms-map --region yul
flyctl secrets set DATABASE_URL=$(flyctl postgres connect carms-pg --app carms-map --json | jq -r '.connection_string')
flyctl secrets set API_KEY=changeme
flyctl deploy
```
Health check: `https://carms-map.fly.dev/health`

### Render (blueprint)
Commit `render.yaml` to the backend repo and click “New + Blueprint” in Render:
```
render services sync
render deploy blueprint
```
Health check: `https://<your-render-host>/health`

### Local container (uses this Dockerfile)
```
docker build -t carms-map .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  carms-map
```
Then open `http://localhost:8000/map` and `http://localhost:8000/docs`.

Notes
- The Dockerfile runs `alembic upgrade head` before starting Uvicorn.
- Adjust `APP_MODULE` if your app lives somewhere else (default: `carms.api.main:app`).
- For Fly/Render, keep the Postgres instance warm; the map relies on gold tables materialized by Dagster.
