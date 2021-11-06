from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.settings import pwd_context
from app.urls.models import UrlModel
from app.users.models import UserModel
from app.users.schemas import UserSigninSchema


def get_user_by_id(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_username(db: Session, user_username: str):
    return db.query(UserModel).filter(UserModel.username == user_username).first()


def get_user_by_email(db: Session, user_email: str):
    return db.query(UserModel).filter(UserModel.email == user_email).first()


def get_user_stats(db: Session, user_id: int):
    urls = (
        db.query(UrlModel)
        .filter(UrlModel.user_id == user_id)
        .options(joinedload("entries"))
    )

    referers = defaultdict(lambda: 0)
    locations = defaultdict(lambda: 0)
    all_clicks = 0

    for url in urls:
        all_clicks += url.clicks
        for entry in url.entries:
            if entry.referer is not None:
                referers[entry.referer] += 1
            if entry.country is not None:
                locations[entry.country] += 1

    return {
        "all_clicks": all_clicks,
        "top_referer": max(referers, key=referers.get, default=None),
        "top_location": max(locations, key=locations.get, default=None),
    }


def create_user(db: Session, user: UserSigninSchema):
    user.password = pwd_context.hash(user.password)
    user = user.dict()
    u = UserModel(**user)
    db.add(u)
    db.commit()
    return u


def is_account_verified(db: Session, user_id: int):
    if (
        db.query(UserModel)
        .filter(UserModel.id == user_id, UserModel.is_active == True)
        .first()
    ):
        return True
    raise HTTPException(status.HTTP_400_BAD_REQUEST, "Account not activated")
