"""HTTP Basic authentication."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from .helpers import ADMIN, make_app, make_client


@pytest.mark.parametrize("url", ["/docs", "/redoc", "/openapi.json"])
def test_missing_credentials_ask_for_basic_auth(url):
    response = make_client().get(url)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Basic"


@pytest.mark.parametrize(
    "auth",
    [("admin", "wrong"), ("nobody", "password123"), ("", ""), ("admin", "")],
)
def test_wrong_credentials_are_rejected(auth):
    response = make_client().get("/docs", auth=auth)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_malformed_authorization_header_is_rejected():
    client = make_client()

    assert (
        client.get("/docs", headers={"Authorization": "Basic !!!"}).status_code == 401
    )
    assert (
        client.get("/docs", headers={"Authorization": "Bearer abc"}).status_code == 401
    )


def test_non_ascii_password_works():
    client = make_client(credentials={"admin": "pässwörd-密码"})
    good = {"Authorization": _basic_header("admin", "pässwörd-密码")}
    bad = {"Authorization": _basic_header("admin", "pässwörd-wrong-密")}

    assert client.get("/docs", headers=good).status_code == 200
    # A wrong non-ASCII password is a 401, not a server error
    assert client.get("/docs", headers=bad).status_code == 401


def test_non_ascii_username_works():
    client = make_client(credentials={"jürgen": "secret"})
    headers = {"Authorization": _basic_header("jürgen", "secret")}

    assert client.get("/openapi.json", headers=headers).status_code == 200


def test_empty_credentials_let_nobody_in():
    client = make_client(credentials={})

    assert client.get("/docs", auth=("", "")).status_code == 401
    assert client.get("/docs", auth=ADMIN).status_code == 401


def test_every_user_can_log_in():
    client = make_client()

    assert client.get("/docs", auth=ADMIN).status_code == 200
    assert client.get("/docs", auth=("dev", "devpass")).status_code == 200


def test_credentials_can_change_at_runtime():
    app, shield = make_app()
    from fastapi.testclient import TestClient

    client = TestClient(app)
    shield.credentials["new"] = "newpass"

    assert client.get("/docs", auth=("new", "newpass")).status_code == 200


def test_verify_credentials_returns_the_username():
    _, shield = make_app()

    credentials = HTTPBasicCredentials(username="admin", password="password123")
    assert shield._verify_credentials(credentials) == "admin"

    with pytest.raises(HTTPException) as error:
        shield._verify_credentials(
            HTTPBasicCredentials(username="admin", password="nope")
        )
    assert error.value.status_code == 401


def test_unknown_auth_method_is_an_error():
    with pytest.raises(ValueError, match="auth_method"):
        make_app(auth_method="token")


def test_protected_responses_are_not_cached():
    client = make_client()

    for url in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(url, auth=ADMIN).headers["Cache-Control"] == "no-store"


def _basic_header(username, password):
    import base64

    token = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
    return f"Basic {token}"
