# Minimal container for the CaRMS FastAPI/map service
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for building psycopg2/geo stack if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest(s) first for better caching
COPY requirements.txt* pyproject.toml* poetry.lock* ./

# Install deps (pip falls back gracefully if files are absent)
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi \
 && if [ -f poetry.lock ]; then pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi; fi

# App source
COPY . .

ENV PORT=8000 \
    APP_MODULE=carms.api.main:app

EXPOSE 8000

# Run migrations then start API
CMD ["bash", "-c", "alembic upgrade head && uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT}"]
