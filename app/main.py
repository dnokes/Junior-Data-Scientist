from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from carms.api.routes import disciplines, pipeline, programs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    from carms.core.database import init_db

    init_db()
    yield
    # shutdown


def create_app() -> FastAPI:
    app = FastAPI(title="CaRMS Platform API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(programs.router)
    app.include_router(disciplines.router)
    app.include_router(pipeline.router)

    class HealthResponse(BaseModel):
        status: str

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return app


app = create_app()
