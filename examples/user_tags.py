"""
Different documentation for different users.

Run with:
    uvicorn examples.user_tags:app --reload

Then open http://localhost:8000/docs:
    admin / admin_password     sees every route
    developer / dev_password   sees only the routes tagged "general"

This only changes what the documentation shows. The routes themselves
still need their own checks.
"""

from fastapi import FastAPI

from fastapi_docshield import DocShield

app = FastAPI(title="Protected API")


@app.get("/", tags=["general"])
def read_root():
    """Return a welcome message."""
    return {"message": "Hello World"}


@app.post("/posts/{post_id}", tags=["admin"])
def create_post(post_id: int):
    """Create a post."""
    return {"id": post_id}


DocShield(
    app=app,
    credentials={
        "admin": "admin_password",
        "developer": "dev_password",
    },
    user_tags={
        "admin": None,  # Sees all routes and schemas
        "developer": ["general"],  # Sees only routes tagged "general"
    },
)
