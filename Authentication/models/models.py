from sqlalchemy import Column, Integer, String

from config import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    national_id = Column(String, unique=True)
    email = Column(String, index=True)
    last_name = Column(String)
    ip = Column(String)
    image1 = Column(String)
    image2 = Column(String)
    state = Column(String, default="pending")
