from fastapi import APIRouter, Depends
from sqlalchemy import text

from typing import Annotated
from models import get_session, Session

router = APIRouter()

@router.get("/")
async def root(session: Annotated[Session, Depends(get_session)]) -> int:
    test_connection = session.exec(text("SELECT 1")).scalar() # type: ignore[attr-defined]
    return test_connection

