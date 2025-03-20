from typing import Any, Generator

from sqlalchemy.orm import declarative_base
from sqlmodel import Session

import state

Base = declarative_base()

def get_session() -> Generator[Session, Any, None]:
    with Session(state.engine) as session:
        yield session

