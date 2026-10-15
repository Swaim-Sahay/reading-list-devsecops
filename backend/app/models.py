from sqlalchemy import Column, DateTime, Integer, String, func

from .database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(120), nullable=False)
    status = Column(String(20), nullable=False, default="to-read")
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
