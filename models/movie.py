from sqlalchemy import Integer
from sqlalchemy import Column, String, Float, DATETIME
from typing import Any
from datetime import datetime

from models import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    rating = Column(Float)
    genres = Column(Integer)
    release_date = Column(DATETIME)
    runtime = Column(Integer)
    available_on = Column(Integer, default=0) 
    youtube_trailer_id = Column(String, nullable=True)

    def as_dict(self) -> dict[str, str]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Movie":
        return cls(
            title=data["original_title"],
            rating=data["vote_average"],
            release_date=datetime.strptime(data["release_date"], "%Y-%m-%d"),
            description=data["overview"],
            runtime=data["runtime"],
        )