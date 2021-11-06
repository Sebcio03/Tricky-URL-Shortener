import pyotp
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.database import get_db
from app.users import crud
from app.users.authentication import authenticate_user
from app.users.email import send_account_verification_mail
from app.users.middleware import login_required
from app.users.models import UserModel
from app.users.schemas import (
    EmailSchema,
    UserDataSchema,
    UserSigninSchema,
    UserSignupSchema,
    UserVerifyWithTOTPSchema,
)

router = APIRouter(prefix="/users", tags=["Signup"])


@router.get("/", response_model=UserDataSchema, response_model_exclude=["password"])
async def get_current_user_data(
    user: UserModel = Depends(login_required), db: Session = Depends(get_db)
):
    stats = crud.get_user_stats(db, user.id)
    return user.__dict__ | stats


@router.post("/", status_code=status.HTTP_201_CREATED)
async def sign_up(
    user: UserSignupSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already exists")

    user = crud.create_user(db, user)
    if user:
        background_tasks.add_task(
            send_account_verification_mail, user.email, user.secret
        )
        return {"detail": "Please verify code"}


@router.post(
    "/code",
    status_code=status.HTTP_201_CREATED,
)
async def verify_account_with_totp(
    user_credentials: UserVerifyWithTOTPSchema,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_email(db, user_credentials.email)
    totp = pyotp.TOTP(user.secret)
    if not user or not totp.verify(user_credentials.code):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "User doesn't exists, or code invalid"
        )
    if user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User is already activated")
    user.is_active = True
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    "/code/resend",
    status_code=status.HTTP_201_CREATED,
)
async def resend_verification_code(
    email: EmailSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email = email.dict()["email"]
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User doesn't exists")
    elif user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already verified")

    background_tasks.add_task(send_account_verification_mail, user.email, user.secret)
    return {"detail": "Please verify code"}


@router.post("/tokens")
async def get_jwt_tokens(
    form_data: UserSigninSchema,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credetials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh")
def get_access_token(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    user_email = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=user_email)
    return {"access_token": access_token}
