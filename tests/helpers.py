"""Small helpers shared by the tests."""

import inspect

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_docshield import DocShield

CREDENTIALS = {"admin": "password123", "dev": "devpass"}
ADMIN = ("admin", "password123")

# Old test clients are built on requests, new ones on httpx. They name the
# "don't follow redirects" argument differently.
_REDIRECT_ARGUMENT = (
    "follow_redirects"
    if "follow_redirects" in inspect.signature(TestClient.get).parameters
    else "allow_redirects"
)
NO_REDIRECT = {_REDIRECT_ARGUMENT: False}


def make_app(app_kwargs=None, **shield_kwargs):
    """Create an app with one route and DocShield on top."""
    app = FastAPI(**{"title": "Test API", **(app_kwargs or {})})

    @app.get("/")
    def read_root():
        return {"message": "Hello World"}

    shield_kwargs.setdefault("credentials", dict(CREDENTIALS))
    shield = DocShield(app=app, **shield_kwargs)
    return app, shield


def make_client(app_kwargs=None, root_path="", **shield_kwargs):
    """
    Create a test client for an app protected by DocShield.

    root_path is the prefix a proxy serves the app under, the way a server
    started with --root-path reports it.
    """
    app, _ = make_app(app_kwargs, **shield_kwargs)
    return TestClient(app, root_path=root_path)
