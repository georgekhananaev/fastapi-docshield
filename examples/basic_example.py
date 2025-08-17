from fastapi import FastAPI
from fastapi_docshield import DocShield

# Create FastAPI app
app = FastAPI(
    title="Protected API",
    description="An API with protected documentation using DocShield v0.2.0",
    version="1.0.0"
)

# Add some routes
@app.get("/")
def read_root():
    """Return a welcome message."""
    return {
        "message": "Welcome to the API! Try accessing /docs with the credentials.",
        "docshield_version": "0.2.0",
        "features": ["Multi-user auth", "CDN fallback", "Custom CSS/JS"]
    }

@app.get("/users")
def get_users():
    """Get a list of sample users."""
    return [
        {"id": 1, "name": "User 1"},
        {"id": 2, "name": "User 2"},
        {"id": 3, "name": "User 3"}
    ]

@app.get("/status")
def get_status():
    """Get API status."""
    return {"status": "online", "protected": True}

# Protect the docs with DocShield v0.2.0
DocShield(
    app=app,
    credentials={
        "admin": "password123",  # Add your credentials here
        "developer": "dev456"    # You can add multiple credential pairs
    },
    
    # New in v0.2.0: CDN fallback is enabled by default
    use_cdn_fallback=True,  # Automatically fallback to local files if CDN fails
    
    # Optional: Add custom styling
    custom_css="""
        /* Add a custom header color */
        .swagger-ui .topbar { background-color: #4a5568; }
    """,
    
    # Optional: Add custom JavaScript
    custom_js="""
        console.log('🛡️ DocShield v0.2.0 - Protected Documentation Loaded');
    """
)

# Run with: uvicorn basic_example:app --reload
# Then try accessing:
# - http://localhost:8000/docs (will require authentication)
# - http://localhost:8000/redoc (will require authentication)