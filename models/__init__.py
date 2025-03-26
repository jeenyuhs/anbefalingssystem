from typing import Any, Generator

from sqlalchemy.orm import declarative_base, sessionmaker, Session

import state

Base = declarative_base()

def get_session() -> Generator[Session, Any, None]:
    Session = sessionmaker(bind=state.engine)

    with Session() as session:
        yield session
