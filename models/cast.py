from sqlalchemy import Integer, String, Column
from typing import Any

from models import Base

class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    def as_dict(self) -> dict[str, Any]:
        return {"actor": self.name, "id": self.id}

class Cast(Base):
    __tablename__ = "cast"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer)
    actor_id = Column(Integer)
    character_name = Column(String)

    def as_dict(self) -> dict[str, Any]:
        return {"character": self.character_name}
    
