from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from carms.core.database import get_session
from carms.models.gold import GoldProgramProfile

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("/", response_model=List[GoldProgramProfile])
def list_programs(
    discipline: Optional[str] = Query(default=None, description="Filter by discipline name"),
    province: Optional[str] = Query(default=None, description="Filter by province code"),
    session: Session = Depends(get_session),
) -> List[GoldProgramProfile]:
    statement = select(GoldProgramProfile)
    if discipline:
        statement = statement.where(GoldProgramProfile.discipline_name.ilike(f"%{discipline}%"))
    if province:
        statement = statement.where(GoldProgramProfile.province == province)

    results = session.exec(statement).all()
    return results
