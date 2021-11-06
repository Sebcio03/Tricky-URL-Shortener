from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.users.crud import get_user_by_email


def login_required(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


def admin_required(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = login_required(Authorize, db)
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
