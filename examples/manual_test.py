"""
Simple test script to manually verify DocShield functionality.
Run with:
    uvicorn manual_test:app --reload
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_docshield import DocShield

app = FastAPI(
    title="DocShield Test App",
    description="Testing API for DocShield",
    version="0.1.0",
)

# Add a simple route
@app.get("/")
def read_root():
    return {"message": "Welcome to the test API. Try accessing /docs with credentials."}

# Protect docs with DocShield
shield = DocShield(
    app=app,
    credentials={
        "admin": "password123",
        "user": "user456"
    }
)

# To test:
# 1. Run the server: uvicorn manual_test:app --reload
# 2. Try accessing the docs endpoints without credentials
#    - http://localhost:8000/docs
#    - http://localhost:8000/redoc
#    - http://localhost:8000/openapi.json
#    All should prompt for Basic Auth
# 3. Enter correct credentials (admin/password123 or user/user456)
#    All should show the respective documentation