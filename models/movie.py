from sqlalchemy import Integer
from sqlalchemy import Column, String, Float, TIMESTAMP

from models import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    rating = Column(Float)
    genres = Column(Integer)
    release_date = Column(TIMESTAMP)

    def as_dict(self) -> dict[str, str]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
