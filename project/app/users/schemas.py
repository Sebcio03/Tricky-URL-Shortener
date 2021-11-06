from enum import Enum

from pydantic import BaseModel
from pydantic.networks import EmailStr

from app import settings


class UseCasesEnum(str, Enum):
    personal_use = "Personal use"
    social_marketing = "Social media marketing"
    influencer_marketing = "Influencer marketing"
    internal_communications = "Internal communications"
    other = "Other"


class UserSigninSchema(BaseModel):
    email: EmailStr
    password: str


class UserSignupSchema(UserSigninSchema):
    username: str
    use_case: UseCasesEnum

    class Config:
        use_enum_values = True
        orm_mode = True


class UserDataSchema(BaseModel):
    username: str
    use_case: UseCasesEnum
    all_clicks: int
    top_referer: str = None
    top_location: str = None

    class Config:
        use_enum_values = True
        orm_mode = True


class UserVerifyWithTOTPSchema(BaseModel):
    email: EmailStr
    code: int


class EmailSchema(BaseModel):
    email: EmailStr


class JWTSettings(BaseModel):
    if settings.DEBUG:
        authjwt_access_token_expires: bool = False
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_decode_algorithms: set = {settings.ALGORITHM}
