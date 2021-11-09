import json
import requests
from app.users.crud import get_user_by_email
from tests.conftest import TestingSessionLocal
import pyotp
from time import sleep
from app.users.models import UserModel


class TestUserViews:
    def setup_method(self, cls):
        self.smtp_server_url = "http://test_smtp:8025/api/v2/messages"
        self.db = TestingSessionLocal()

    def teardown_method(self, cls):
        self.db.close()

    def test_signup_user(self, client):
        emails = requests.get(self.smtp_server_url).json()["count"]

        response = client.post(
            "/users/",
            json={
                "email": "user1@example.com",
                "password": "string",
                "username": "string",
                "use_case": "Personal use",
            },
        )

        assert response.status_code == 201
        assert response.json() == {"detail": "Please verify code"}

        user = get_user_by_email(self.db, "user1@example.com")
        assert user is not None
        assert user.secret is not None

        emails_after_signup = requests.get(self.smtp_server_url).json()["items"]
        totp = pyotp.TOTP(user.secret)
        email_headers = emails_after_signup[0]["Content"]["Headers"]
        email_subject = email_headers["Subject"][0]
        email_recipent = email_headers["To"][0]
        assert email_recipent == "user1@example.com"
        code = email_subject.split("code ")[1]
        assert totp.verify(code) == True
        assert emails < len(emails_after_signup), "Email wasn't send"

    def test_signup_user_with_already_existing_email(self, client):
        response = client.post(
            "/users/",
            json={
                "email": "user1@example.com",
                "password": "string",
                "username": "string",
                "use_case": "Personal use",
            },
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Email already exists"}
        users = (
            self.db.query(UserModel)
            .filter(UserModel.email == "user1@example.com")
            .all()
        )
        assert len(users) == 1

    def test_resend_code(self, client):
        emails = requests.get(self.smtp_server_url).json()["count"]

        response = client.post(
            "/users/code/resend", json={"email": "user1@example.com"}
        )

        assert response.status_code == 201
        assert response.json() == {"detail": "Please verify code"}

        user = get_user_by_email(self.db, "user1@example.com")
        emails_after_signup = requests.get(self.smtp_server_url).json()["items"]
        totp = pyotp.TOTP(user.secret)
        email_headers = emails_after_signup[0]["Content"]["Headers"]
        email_subject = email_headers["Subject"][0]
        email_recipent = email_headers["To"][0]
        assert email_recipent == "user1@example.com"
        code = email_subject.split("code ")[1]
        assert totp.verify(code) == True
        assert emails < len(emails_after_signup), "Email wasn't send"

    def test_get_user_tokens_with_not_activated_account(self, client):
        response = client.post(
            "/users/tokens", json={"email": "user1@example.com", "password": "string"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Account not activated"}
        user = get_user_by_email(self.db, "user1@example.com")
        assert user.is_active == False

    def test_verify_user_with_wrong_code(self, client):
        response = client.post(
            "/users/code",
            json={"email": "user1@example.com", "code": "123"},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "User doesn't exists, or code invalid"}

    def test_verify_user_with_good_code(self, client):
        emails = requests.get(self.smtp_server_url).json()["items"]
        last_email_subject = emails[0]["Content"]["Headers"]["Subject"][0]
        code = last_email_subject.split("code ")[1]
        response = client.post(
            "/users/code",
            json={"email": "user1@example.com", "code": str(code)},
        )
        assert response.status_code == 201
        user = get_user_by_email(self.db, "user1@example.com")
        assert user.is_active == True

    def test_verify_user_with_already_verified_user(self, client):
        emails = requests.get(self.smtp_server_url).json()["items"]
        last_email_body_subject = emails[0]["Content"]["Headers"]["Subject"][0]
        code = last_email_body_subject.split("code ")[1]

        user = get_user_by_email(self.db, "user1@example.com")
        assert user.is_active == True
        response = client.post(
            "/users/code",
            json={"email": "user1@example.com", "code": str(code)},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "User is already activated"}
        user = get_user_by_email(self.db, "user1@example.com")
        assert user.is_active == True

    def test_resend_code_with_alredy_verified_user(self, client):
        response = client.post(
            "/users/code/resend", json={"email": "user1@example.com"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "User already verified"}

    def test_get_user_tokens_with_activated_user(self, client):
        response = client.post(
            "/users/tokens", json={"email": "user1@example.com", "password": "string"}
        )
        json_response = response.json()
        user = get_user_by_email(self.db, "user1@example.com")
        assert user.is_active == True
        assert response.status_code == 200
        assert len(json_response.keys()) == 2
        assert "access_token" in json_response
        assert "refresh_token" in json_response

    def test_get_user_refresh_token(self, client):
        refresh_token = client.post(
            "/users/tokens", json={"email": "user1@example.com", "password": "string"}
        ).json()["refresh_token"]
        response = client.post(
            "/users/refresh",
            headers={"Authorization": "Bearer  " + refresh_token},
        )
        assert response.status_code == 200
        assert len(response.json().keys()) == 1

    def test_get_user_data(self, client):
        response_json = client.post(
            "/users/tokens", json={"email": "user1@example.com", "password": "string"}
        ).json()
        response = client.get(
            "/users/",
            headers={"Authorization": "Bearer  " + response_json["access_token"]},
        )
        assert response.status_code == 200
        assert len(response.json().keys()) == 5