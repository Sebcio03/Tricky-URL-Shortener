import os

from fastapi_mail import ConnectionConfig
from hashids import Hashids
from jinja2 import Environment, PackageLoader, select_autoescape
from passlib.context import CryptContext

DEBUG = bool(int(os.environ["DEBUG"]))
DOMAIN = os.environ["DOMAIN"]
hashids = Hashids(salt=os.environ["SALT"])

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

DATABASE_CREDENTIALS = {
    "drivername": "postgresql+psycopg2",
    "username": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "postgres"),
    "host": os.environ.get("POSTGRES_HOST", "db"),
    "port": os.environ.get("POSTGRES_PORT", 5432),
    "database": os.environ.get("POSTGRES_DB", "postgres"),
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


conf = ConnectionConfig(
    MAIL_USERNAME=os.environ["MAIL_USERNAME"],
    MAIL_PASSWORD=os.environ["MAIL_PASSWORD"],
    MAIL_FROM=os.environ["MAIL_FROM"],
    MAIL_PORT=os.environ["MAIL_PORT"],
    MAIL_SERVER=os.environ["MAIL_SERVER"],
    MAIL_TLS=os.environ["MAIL_TLS"],
    MAIL_SSL=os.environ["MAIL_SSL"],
    USE_CREDENTIALS=os.environ["MAIL_USE_CREDENTIALS"],
)

env = Environment(
    loader=PackageLoader("app", "templates/"), autoescape=select_autoescape()
)

AWS_BUCKET_HOST = os.environ["AWS_BUCKET_HOST"]
AWS_BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
