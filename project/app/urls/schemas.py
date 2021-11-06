from datetime import datetime
from typing import List

from pydantic import BaseModel, HttpUrl, IPvAnyAddress


class EntrySchema(BaseModel):
    full_user_agent: str
    referer: HttpUrl = None
    os: str
    browser: str
    country: str = ""
    lat: float = 0
    lon: float = ""
    ip: IPvAnyAddress


class UrlInSchema(BaseModel):
    title: str = None
    shorten: str = None
    redirect_to: HttpUrl


class UrlOutSchema(UrlInSchema):
    id: int
    clicks: int
    creation_date: datetime


class UrlDetailSchema(UrlOutSchema):
    entries: List[EntrySchema] = []
