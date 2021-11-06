from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app import settings
from app.users import crud
from app.users.schemas import JWTSettings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


@AuthJWT.load_config
def get_config():
    if settings.DEBUG:
        return JWTSettings(authjwt_access_token_expires=False)
    return JWTSettings()


def verify_password(plain_password, hashed_password):
    return settings.pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return settings.pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return False
    if not crud.is_account_verified(db, user.id):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account not activated")
    return user
