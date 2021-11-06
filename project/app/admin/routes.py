from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.users.middleware import admin_required
from app.users.models import UserModel

from .crud import get_all_crawled_data, get_crawled_data_by_id
from .schemas import AllCrawledDataResponseSchema, CrawledDataResponseSchema

router = APIRouter(prefix="/crawled-data", tags=["Admin"])


@router.get("/", response_model=List[AllCrawledDataResponseSchema])
async def get_all_crawled_data(
    admin: UserModel = Depends(admin_required),
    db: Session = Depends(get_db),
):
    data = get_all_crawled_data(db)
    return jsonable_encoder(data)


@router.get("/{crawled_data_id}", response_model=CrawledDataResponseSchema)
async def get_crawled_data(
    crawled_data_id: int,
    admin: UserModel = Depends(admin_required),
    db: Session = Depends(get_db),
):
    data = get_crawled_data_by_id(db, crawled_data_id)
    return jsonable_encoder(data)
