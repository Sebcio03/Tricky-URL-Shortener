import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.settings import DATABASE_CREDENTIALS
from app.users.crud import create_user

db_url = URL.create(**DATABASE_CREDENTIALS)
engine = create_engine(db_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        db.rollback()
        db.commit()


# @pytest.fixture()
# def create_verified_user(create_basic_user):
#     emails = requests.get("http://test_smtp:8025/api/v2/messages").json()["items"]
#     last_email_body_subject = emails[0]["Content"]["Headers"]["Subject"][0]
#     code = last_email_body_subject.split("code ")[1]
#     response = client.post(
#         "/users/code",
#         json={"email": "user@example.com", "code": code},
#     )
#     return response


# @pytest.fixture()
# def user_tokens(create_verified_user):
#     response = client.post(
#         "/users/tokens", json={"email": "user@example.com", "password": "string"}
#     )
#     return response.json()
