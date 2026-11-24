"""
A login page instead of the browser's password prompt, with a "Log out" link.

Run with:
    uvicorn examples.form_login:app --reload

Then open http://localhost:8000/docs and log in with admin / password123.
"""

from fastapi import FastAPI

from fastapi_docshield import DocShield

app = FastAPI(title="Protected API")


@app.get("/")
def read_root():
    """Return a welcome message."""
    return {"message": "Welcome! The documentation at /docs needs a login."}


DocShield(
    app=app,
    credentials={"admin": "password123"},
    auth_method="form",
    # A session lasts 8 hours by default. This one lasts 30 minutes.
    session_max_age=30 * 60,
)
