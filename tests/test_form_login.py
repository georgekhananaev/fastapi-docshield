"""Form login: the login page, the session cookie and logout."""

import time

import pytest
from fastapi.testclient import TestClient

from fastapi_docshield.docshield import SESSION_COOKIE_NAME

from .helpers import ADMIN, NO_REDIRECT, make_app, make_client

LOGIN = "/docshield/login"
LOGOUT = "/docshield/logout"


def form_client(**kwargs):
    return make_client(auth_method="form", **kwargs)


def log_in(client, username="admin", password="password123", next_url=None):
    data = {"username": username, "password": password}
    if next_url is not None:
        data["next"] = next_url
    return client.post(LOGIN, data=data, **NO_REDIRECT)


@pytest.mark.parametrize("url", ["/docs", "/redoc"])
def test_pages_redirect_to_the_login_page(url):
    response = form_client().get(url, **NO_REDIRECT)

    assert response.status_code == 303
    assert response.headers["location"] == f"{LOGIN}?next={url}"
    assert "WWW-Authenticate" not in response.headers


def test_openapi_answers_401_without_a_browser_prompt():
    response = form_client().get("/openapi.json")

    assert response.status_code == 401
    assert "WWW-Authenticate" not in response.headers


def test_login_page_shows_a_form():
    response = form_client().get(LOGIN)

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert f'<form method="post" action="{LOGIN}">' in response.text
    assert 'name="username"' in response.text
    assert 'type="password"' in response.text
    assert "Test API" in response.text
    assert "Incorrect username or password" not in response.text


def test_login_page_escapes_the_title():
    client = form_client(app_kwargs={"title": "<b>API</b>"})

    assert "<b>API</b>" not in client.get(LOGIN).text


@pytest.mark.parametrize(
    "username, password",
    [("admin", "wrong"), ("nobody", "password123"), ("", "")],
)
def test_wrong_login_shows_an_error(username, password):
    client = form_client()

    response = log_in(client, username, password)

    assert response.status_code == 401
    assert "Incorrect username or password" in response.text
    assert "set-cookie" not in response.headers
    assert client.get("/docs", **NO_REDIRECT).status_code == 303


def test_login_opens_the_docs():
    client = form_client()

    response = log_in(client)

    assert response.status_code == 303
    assert response.headers["location"] == "/docs"
    cookie = response.headers["set-cookie"].lower()
    assert cookie.startswith(SESSION_COOKIE_NAME + "=")
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "secure" not in cookie
    assert "path=/" in cookie

    docs = client.get("/docs", **NO_REDIRECT)
    assert docs.status_code == 200
    assert "swagger-ui" in docs.text
    assert client.get("/redoc", **NO_REDIRECT).status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_docs_pages_have_a_logout_link():
    client = form_client()
    log_in(client)

    for url in ("/docs", "/redoc"):
        assert f'class="docshield-logout" href="{LOGOUT}"' in client.get(url).text


def test_basic_auth_pages_have_no_logout_link():
    page = make_client().get("/docs", auth=ADMIN).text

    assert "docshield-logout" not in page


def test_login_returns_to_the_page_that_was_asked_for():
    client = form_client()

    assert 'name="next" value="/redoc"' in client.get(f"{LOGIN}?next=/redoc").text
    assert log_in(client, next_url="/redoc").headers["location"] == "/redoc"


@pytest.mark.parametrize(
    "next_url", ["https://evil.example/", "//evil.example/", "/other", ""]
)
def test_login_never_redirects_to_another_site(next_url):
    client = form_client()

    assert log_in(client, next_url=next_url).headers["location"] == "/docs"
    assert "evil.example" not in client.get(f"{LOGIN}?next={next_url}").text


def test_login_target_without_docs_pages():
    client = form_client(app_kwargs={"docs_url": None})
    assert log_in(client).headers["location"] == "/redoc"

    client = form_client(app_kwargs={"docs_url": None, "redoc_url": None})
    assert log_in(client).headers["location"] == "/openapi.json"


def test_logged_in_user_skips_the_login_page():
    client = form_client()
    log_in(client)

    response = client.get(f"{LOGIN}?next=/redoc", **NO_REDIRECT)

    assert response.status_code == 303
    assert response.headers["location"] == "/redoc"


def test_logout_ends_the_session():
    client = form_client()
    log_in(client)
    assert client.get("/docs", **NO_REDIRECT).status_code == 200

    response = client.get(LOGOUT, **NO_REDIRECT)

    assert response.status_code == 303
    assert response.headers["location"] == LOGIN
    assert client.get("/docs", **NO_REDIRECT).status_code == 303
    assert client.get("/openapi.json").status_code == 401


def test_basic_auth_still_works_with_form_login():
    client = form_client()

    assert client.get("/openapi.json", auth=ADMIN).status_code == 200
    assert client.get("/docs", auth=ADMIN, **NO_REDIRECT).status_code == 200
    assert client.get("/openapi.json", auth=("admin", "wrong")).status_code == 401


def test_session_round_trip():
    _, shield = make_app(auth_method="form", credentials={"jürgen": "pässwort"})

    token = shield._create_session("jürgen")

    assert shield._read_session(token) == "jürgen"
    assert "=" not in token


@pytest.mark.parametrize(
    "token",
    [None, "", "abc", "a.b.c", "..", "YWRtaW4.9999999999.deadbeef", "ä.ö.ü"],
)
def test_invalid_session_tokens_are_rejected(token):
    _, shield = make_app(auth_method="form")

    assert shield._read_session(token) is None


def test_tampered_session_is_rejected():
    _, shield = make_app(auth_method="form")
    user, expires, signature = shield._create_session("dev").split(".")
    admin = shield._create_session("admin").split(".")[0]

    assert shield._read_session(f"{admin}.{expires}.{signature}") is None
    assert shield._read_session(f"{user}.{int(expires) + 60}.{signature}") is None


def test_malformed_payload_with_a_valid_signature_is_rejected():
    _, shield = make_app(auth_method="form")

    for payload in ("YWRtaW4.soon", "####.9999999999"):
        assert shield._read_session(f"{payload}.{shield._sign(payload)}") is None


def test_expired_session_is_rejected():
    _, shield = make_app(auth_method="form", session_max_age=-10)

    assert shield._read_session(shield._create_session("admin")) is None


def test_session_lifetime_is_set_on_the_cookie():
    app, shield = make_app(auth_method="form", session_max_age=600)
    client = TestClient(app)

    cookie = log_in(client).headers["set-cookie"].lower()
    expires = int(client.cookies.get(SESSION_COOKIE_NAME).split(".")[1])

    assert "max-age=600" in cookie
    assert 590 <= expires - time.time() <= 600


def test_changed_password_ends_the_session():
    app, shield = make_app(auth_method="form")
    client = TestClient(app)
    log_in(client)

    shield.credentials["admin"] = "a-new-password"

    assert client.get("/docs", **NO_REDIRECT).status_code == 303


def test_removed_user_loses_the_session():
    app, shield = make_app(auth_method="form")
    token = shield._create_session("dev")
    assert shield._read_session(token) == "dev"

    del shield.credentials["dev"]

    assert shield._read_session(token) is None


def test_sessions_need_the_same_secret():
    _, first = make_app(auth_method="form", session_secret="one")
    _, second = make_app(auth_method="form", session_secret=b"two")
    _, third = make_app(auth_method="form", session_secret="one")
    token = first._create_session("admin")

    assert second._read_session(token) is None
    assert third._read_session(token) == "admin"


def test_too_large_login_body_is_rejected():
    client = form_client()

    response = log_in(client, password="password123" + "x" * 10000)

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_user_tags_apply_to_a_session():
    client = form_client(user_tags={"dev": ["nothing"]})
    log_in(client, "dev", "devpass")

    assert client.get("/openapi.json").json()["paths"] == {}


def test_custom_login_and_logout_urls():
    client = form_client(login_url="/sign-in", logout_url="/sign-out")

    assert (
        client.get("/docs", **NO_REDIRECT).headers["location"] == "/sign-in?next=/docs"
    )
    assert client.get("/sign-in").status_code == 200
    response = client.post(
        "/sign-in", data={"username": "admin", "password": "password123"}, **NO_REDIRECT
    )
    assert response.status_code == 303
    assert 'href="/sign-out"' in client.get("/docs").text
    assert client.get("/sign-out", **NO_REDIRECT).headers["location"] == "/sign-in"
    assert client.get(LOGIN).status_code == 404


def test_form_login_behind_a_root_path():
    client = form_client(root_path="/api")

    redirect = client.get("/docs", **NO_REDIRECT)
    assert redirect.headers["location"] == "/api/docshield/login?next=/docs"
    assert 'action="/api/docshield/login"' in client.get(LOGIN).text

    response = log_in(client)
    assert response.headers["location"] == "/api/docs"
    assert "path=/api" in response.headers["set-cookie"].lower()

    logout = client.get(LOGOUT, **NO_REDIRECT)
    assert logout.headers["location"] == "/api/docshield/login"


def test_basic_mode_has_no_login_routes():
    client = make_client()

    assert client.get(LOGIN).status_code == 404
    assert client.get(LOGOUT, **NO_REDIRECT).status_code == 404
