from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from carms.core.database import get_session
from carms.models.silver import SilverDiscipline

router = APIRouter(prefix="/disciplines", tags=["disciplines"])


@router.get("/", response_model=List[SilverDiscipline])
def list_disciplines(session: Session = Depends(get_session)) -> List[SilverDiscipline]:
    statement = select(SilverDiscipline).where(SilverDiscipline.is_valid == True)  # noqa: E712
    return session.exec(statement).all()
