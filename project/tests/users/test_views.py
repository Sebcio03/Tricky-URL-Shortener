import requests


class TestUserViews:
    def test_signup_user_without_verification(self, client):
        emails = requests.get("http://test_smtp:8025/api/v2/messages").json()["items"]

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

        emails_after_signup = requests.get(
            "http://test_smtp:8025/api/v2/messages"
        ).json()["items"]
        assert len(emails) <= len(emails_after_signup), "Email wasn't send"

    def test_signup_user_with_email_already_exists(self, client):
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

    def test_resend_code(self, client):
        emails = requests.get("http://test_smtp:8025/api/v2/messages").json()["items"]

        response = client.post(
            "/users/code/resend", json={"email": "user1@example.com"}
        )

        assert response.status_code == 201
        assert response.json() == {"detail": "Please verify code"}

        emails_after_resend = requests.get(
            "http://test_smtp:8025/api/v2/messages"
        ).json()["items"]
        assert len(emails) <= len(emails_after_resend), "Email wasn't send"

    def test_get_user_tokens_with_account_not_activated(self, client):
        response = client.post(
            "/users/tokens", json={"email": "user1@example.com", "password": "string"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Account not activated"}

    def test_verify_user_with_wrong_code(self, client):
        response = client.post(
            "/users/code",
            json={"email": "user1@example.com", "code": "123"},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "User doesn't exists, or code invalid"}

    def test_verify_user_success(self, client):
        emails = requests.get("http://test_smtp:8025/api/v2/messages").json()["items"]
        last_email_body_subject = emails[0]["Content"]["Headers"]["Subject"][0]
        code = last_email_body_subject.split("code ")[1]
        response = client.post(
            "/users/code",
            json={"email": "user1@example.com", "code": str(code)},
        )
        assert response.status_code == 201

    def test_verify_user_with_already_verified_user(self, client):
        emails = requests.get("http://test_smtp:8025/api/v2/messages").json()["items"]
        last_email_body_subject = emails[0]["Content"]["Headers"]["Subject"][0]
        code = last_email_body_subject.split("code ")[1]
        response = client.post(
            "/users/code",
            json={"email": "user1@example.com", "code": str(code)},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "User is already activated"}

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
        assert response.status_code == 200
        assert len(json_response.keys()) == 2
        assert json_response["access_token"]
        assert json_response["refresh_token"]

    def test_get_user_refresh_token(self, client):
        refresh_token = client.post(
            "/users/tokens", json={"email": "user1@example.com", "password": "string"}
        ).json()["refresh_token"]
        response = client.post("/users/tokens", json={"refresh_token": refresh_token})

    def test_get_user_data(self, client):
        response_json = client.post(
            "/users/tokens", json={"email": "user1@example.com", "password": "string"}
        ).json()
        access_token = response_json["access_token"]
        response = client.get(
            "/users/", headers={"Authorization": "Bearer " + access_token}
        )
        assert response.status_code == 200
        assert len(response.json().keys()) == 5
