from sqlalchemy import Integer, String, Column
from typing import Any

from models import Base

class Actor(Base):
    __tablename__ = "actors"


    id = Column(Integer, primary_key=True)
    name = Column(String)

    def as_dict(self) -> dict[str, Any]:
        return {"actor": self.name, "id": self.id}

class Cast(Base):
    __tablename__ = "cast"

    movie_id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, primary_key=True)
    character_name = Column(String)

    def as_dict(self) -> dict[str, Any]:
        return {"character": self.character_name}

