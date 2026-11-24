"""The app that tests/test_integration.py starts in a real server."""

from fastapi import FastAPI

from fastapi_docshield import DocShield

app = FastAPI(title="DocShield Test App")


@app.get("/")
def read_root():
    return {"message": "Welcome to the DocShield test API"}


DocShield(app=app, credentials={"admin": "password123", "user": "user456"})
