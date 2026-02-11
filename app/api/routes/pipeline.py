import subprocess
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class PipelineRunResponse(BaseModel):
    status: Literal["success", "error"]
    detail: str


@router.post("/run", response_model=PipelineRunResponse)
def run_pipeline() -> PipelineRunResponse:
    """Trigger the Dagster asset job via subprocess."""
    command = [
        "dagster",
        "job",
        "execute",
        "-m",
        "carms.pipelines.definitions",
        "-j",
        "carms_job",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    status: Literal["success", "error"] = "success" if result.returncode == 0 else "error"
    detail = result.stdout if status == "success" else (result.stderr or result.stdout)
    return PipelineRunResponse(status=status, detail=detail[-2000:])
