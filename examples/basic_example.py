"""
The smallest setup: HTTP Basic Auth on /docs, /redoc and /openapi.json.

Run with:
    uvicorn examples.basic_example:app --reload

Then open http://localhost:8000/docs and log in with admin / password123.
"""

from fastapi import FastAPI

from fastapi_docshield import DocShield

app = FastAPI(title="Protected API")


@app.get("/")
def read_root():
    """Return a welcome message."""
    return {"message": "Welcome! The documentation at /docs needs a login."}


@app.get("/users")
def get_users():
    """Get a list of sample users."""
    return [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]


DocShield(
    app=app,
    credentials={
        "admin": "password123",
        "developer": "dev456",
    },
)
