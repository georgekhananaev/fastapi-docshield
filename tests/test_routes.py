"""Which routes DocShield adds, removes and leaves alone."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_docshield import DocShield

from .helpers import ADMIN, CREDENTIALS, make_app, make_client


def test_routes_under_the_docs_path_are_kept():
    app = FastAPI()

    @app.get("/docs/guide")
    def guide():
        return {"page": "guide"}

    @app.get("/redoc-notes")
    def notes():
        return {"page": "notes"}

    DocShield(app=app, credentials=CREDENTIALS)
    client = TestClient(app)

    assert client.get("/docs/guide").json() == {"page": "guide"}
    assert client.get("/redoc-notes").json() == {"page": "notes"}


def test_custom_urls_replace_the_default_ones():
    client = make_client(
        docs_url="/custom-docs",
        redoc_url="/custom-redoc",
        openapi_url="/custom-openapi.json",
    )

    for url in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(url, auth=ADMIN).status_code == 404
    for url in ("/custom-docs", "/custom-redoc", "/custom-openapi.json"):
        assert client.get(url).status_code == 401
        assert client.get(url, auth=ADMIN).status_code == 200
    assert "/custom-openapi.json" in client.get("/custom-docs", auth=ADMIN).text


def test_app_with_its_own_docs_urls_is_protected():
    client = make_client(app_kwargs={"docs_url": "/swagger", "redoc_url": "/reference"})

    # The app's original, unprotected pages are gone
    assert client.get("/swagger").status_code == 404
    assert client.get("/reference").status_code == 404
    assert client.get("/docs").status_code == 401


def test_disabled_docs_stay_disabled():
    client = make_client(app_kwargs={"docs_url": None})

    assert client.get("/docs", auth=ADMIN).status_code == 404
    assert client.get("/redoc", auth=ADMIN).status_code == 200
    assert client.get("/openapi.json", auth=ADMIN).status_code == 200


def test_disabled_redoc_stays_disabled():
    client = make_client(app_kwargs={"redoc_url": None})

    assert client.get("/redoc", auth=ADMIN).status_code == 404
    assert client.get("/docs", auth=ADMIN).status_code == 200


def test_built_in_docs_are_switched_off_on_the_app():
    app, shield = make_app()

    assert (app.docs_url, app.redoc_url, app.openapi_url) == (None, None, None)
    assert shield.original_docs_url == "/docs"
    assert shield.original_redoc_url == "/redoc"
    assert shield.original_openapi_url == "/openapi.json"


def test_swagger_oauth2_redirect_page_still_works():
    client = make_client()

    response = client.get("/docs/oauth2-redirect")

    assert response.status_code == 200
    assert "oauth2" in response.text.lower()
    assert "/docs/oauth2-redirect" in client.get("/docs", auth=ADMIN).text


def test_docshield_routes_are_not_in_the_schema():
    client = make_client(auth_method="form")

    paths = client.get("/openapi.json", auth=ADMIN).json()["paths"]

    assert list(paths) == ["/"]


def test_app_routes_keep_working():
    client = make_client()

    assert client.get("/").json() == {"message": "Hello World"}
