from models import Base

from sqlalchemy import Integer, String, Column

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    display_name  = Column(String)

    def as_dict(self) -> dict[str, str]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
