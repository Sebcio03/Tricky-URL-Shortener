from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class EntryModel(Base):
    __tablename__ = "Entry"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("Url.id"))
    url = relationship("UrlModel", back_populates="entries")
    full_user_agent = Column(String)
    referer = Column(String, nullable=True)
    os = Column(String)
    browser = Column(String)
    ip = Column(String)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    country = Column(String, nullable=True)
    datetime = Column(DateTime, default=datetime.now)
