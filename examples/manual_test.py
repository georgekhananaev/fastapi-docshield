"""
Simple test script to manually verify DocShield v0.2.0 functionality.
Run with:
    uvicorn manual_test:app --reload
"""
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI(
    title="DocShield Test App",
    description="Testing API for DocShield v0.2.0 with all new features",
    version="0.2.0",
)

# Add test routes
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the DocShield v0.2.0 test API",
        "docs": "/docs (protected)",
        "redoc": "/redoc (protected)",
        "features": {
            "cdn_fallback": "Enabled by default",
            "custom_styling": "Supported",
            "multi_user": "Supported"
        }
    }

@app.get("/test")
def test_endpoint():
    return {"test": "successful", "version": "0.2.0"}

# Test different configuration options
# Uncomment different configurations to test various features

# Configuration 1: Basic protection with defaults
shield = DocShield(
    app=app,
    credentials={
        "admin": "password123",
        "user": "user456"
    }
)

# Configuration 2: With custom styling (uncomment to test)
# shield = DocShield(
#     app=app,
#     credentials={
#         "admin": "password123",
#         "user": "user456"
#     },
#     custom_css="""
#         .swagger-ui { background: #f0f0f0; }
#         .swagger-ui .topbar { background: #333; }
#     """,
#     custom_js="console.log('Custom JS loaded!');"
# )

# Configuration 3: Prefer local files (uncomment to test)
# shield = DocShield(
#     app=app,
#     credentials={
#         "admin": "password123",
#         "user": "user456"
#     },
#     prefer_local=True  # Always use bundled static files
# )

# Configuration 4: No CDN fallback (uncomment to test)
# shield = DocShield(
#     app=app,
#     credentials={
#         "admin": "password123",
#         "user": "user456"
#     },
#     use_cdn_fallback=False  # CDN only, no fallback
# )

# To test:
# 1. Run the server: uvicorn manual_test:app --reload
# 2. Try accessing the docs endpoints without credentials
#    - http://localhost:8000/docs
#    - http://localhost:8000/redoc
#    - http://localhost:8000/openapi.json
#    All should prompt for Basic Auth
# 3. Enter correct credentials (admin/password123 or user/user456)
#    All should show the respective documentation