import datetime
from typing import List

from pydantic import BaseModel, HttpUrl


class AllCrawledDataResponseSchema(BaseModel):
    id: str
    url: HttpUrl
    html: str
    creation_date: datetime.datetime


class EmailSchema(BaseModel):
    id: int
    value: str


class ImageSchema(BaseModel):
    id: int
    value: str


class CrawledDataResponseSchema(AllCrawledDataResponseSchema):
    emails: List[EmailSchema] = []
    images: List[str] = []
