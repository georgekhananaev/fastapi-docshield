from fastapi import FastAPI
from fastapi_docshield import DocShield

# Create FastAPI app
app = FastAPI(
    title="Protected API",
    description="An API with protected documentation",
    version="1.0.0"
)

# Add some routes
@app.get("/")
def read_root():
    """Return a welcome message."""
    return {"message": "Welcome to the API! Try accessing /docs with the credentials."}

@app.get("/users")
def get_users():
    """Get a list of sample users."""
    return [
        {"id": 1, "name": "User 1"},
        {"id": 2, "name": "User 2"},
        {"id": 3, "name": "User 3"}
    ]

# Protect the docs with DocShield
DocShield(
    app=app,
    credentials={
        "admin": "password123",  # Add your credentials here
        "developer": "dev456"    # You can add multiple credential pairs
    }
)

# Run with: uvicorn basic_example:app --reload
# Then try accessing:
# - http://localhost:8000/docs (will require authentication)
# - http://localhost:8000/redoc (will require authentication)