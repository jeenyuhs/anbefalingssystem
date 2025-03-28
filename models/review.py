from sqlalchemy import Column, Integer, String, TIMESTAMP

from models import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer)
    user_id = Column(Integer)
    title = Column(String)
    description = Column(String)
    likes = Column(Integer)
    created_at = Column(TIMESTAMP)

    def as_dict(self) -> dict[str, str]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
