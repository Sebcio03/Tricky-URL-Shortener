from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.urls.tasks import crawl_url
from app.users.middleware import login_required
from app.users.models import UserModel

from .crud import create_url_shortener, get_url, get_user_urls
from .schemas import UrlDetailSchema, UrlInSchema, UrlOutSchema

router = APIRouter(prefix="/urls", tags=["Urls"])


@router.post("/", response_model=UrlOutSchema)
async def create_url(
    url: UrlInSchema,
    background_tasks: BackgroundTasks,
    user: UserModel = Depends(login_required),
    db: Session = Depends(get_db),
):
    try:
        url = create_url_shortener(db, user.id, url.dict())
    except IntegrityError:
        raise HTTPException(
            detail="Shorten already exists", status_code=status.HTTP_400_BAD_REQUEST
        )

    background_tasks.add_task(crawl_url, url.redirect_to)
    return jsonable_encoder(url)


@router.get("/", response_model=List[UrlOutSchema])
async def get_all_urls(
    user: UserModel = Depends(login_required), db: Session = Depends(get_db)
):
    urls = get_user_urls(db, user.id)
    return jsonable_encoder(urls)


@router.get("/{shorten}", response_model=UrlDetailSchema)
async def get_particular_url(
    shorten: str,
    user: UserModel = Depends(login_required),
    db: Session = Depends(get_db),
):
    url = get_url(db, user.id, shorten)
    if not url:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return jsonable_encoder(url)
