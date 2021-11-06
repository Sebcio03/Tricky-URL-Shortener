from datetime import datetime

import pyotp
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class UserModel(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256))
    email = Column(String(254), unique=True)
    password = Column(String(128))
    use_case = Column(String(100))

    date_of_creation = Column(DateTime, default=datetime.now)
    secret = Column(String, default=pyotp.random_base32)

    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    urls = relationship("UrlModel")
