from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.sqltypes import Boolean

from app.database import Base

crawled2email_association = Table(
    "crawled2email",
    Base.metadata,
    Column("crawled_data_id", ForeignKey("crawled_data.id")),
    Column("email_id", ForeignKey("email.id")),
)


class ImageModel(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    value = Column(String(64), unique=True)
    crawled_data_id = Column(Integer, ForeignKey("crawled_data.id"))


class EmailModel(Base):
    __tablename__ = "email"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    value = Column(String, unique=True)


class CrawledData(Base):
    __tablename__ = "crawled_data"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    url = Column(String)
    html = Column(Text)
    creation_date = Column(DateTime, default=datetime.now)
    emails = relationship("EmailModel", secondary=crawled2email_association)
    images = relationship("ImageModel")


class UrlModel(Base):
    __tablename__ = "Url"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
    )
    shorten = Column(String)
    title = Column(String)
    redirect_to = Column(String)
    creation_date = Column(DateTime, default=datetime.now)

    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("User.id"))
    entries = relationship("EntryModel", back_populates="url")
