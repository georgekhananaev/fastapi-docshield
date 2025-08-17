from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi_docshield import DocShield

# Create FastAPI app
app = FastAPI(
    title="Advanced Protected API",
    description="An API with protected documentation and custom paths",
    version="1.0.0"
)

# Simple user database for the API routes (not related to DocShield)
fake_users_db = {
    "user1": {
        "username": "user1",
        "email": "user1@example.com",
        "password": "secret1",
    },
    "user2": {
        "username": "user2",
        "email": "user2@example.com",
        "password": "secret2",
    },
}

# OAuth2 token endpoint for the API (not related to DocShield)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str

class UserInDB(User):
    password: str

# API routes (not related to DocShield)
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": user["username"], "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    if token not in fake_users_db:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = fake_users_db[token]
    return user

# Protect the docs with DocShield - showcasing various features
DocShield(
    app=app,
    credentials={
        "admin": "admin123",  # Credentials for accessing the docs
        "dev": "dev456"       # Multiple users supported
    },
    docs_url="/api/docs",              # Custom docs URL 
    redoc_url="/api/redoc",            # Custom redoc URL
    openapi_url="/api/openapi.json",   # Custom OpenAPI JSON URL
    
    # New in v0.2.0: CDN fallback options
    use_cdn_fallback=True,  # Automatically fallback to local files if CDN fails (default: True)
    prefer_local=False,     # Set to True to always use local files instead of CDN
    
    # New in v0.2.0: Custom CSS and JavaScript injection
    custom_css="""
        /* Custom branding example */
        .swagger-ui .topbar { 
            background-color: #2c3e50; 
        }
        .swagger-ui .topbar .download-url-wrapper { 
            display: none; 
        }
    """,
    custom_js="""
        console.log('Advanced API Documentation Loaded');
        // Add custom functionality here
    """
)

# Run with: uvicorn advanced_example:app --reload
# Then try accessing:
# - http://localhost:8000/api/docs (protected with DocShield credentials)
# - http://localhost:8000/api/redoc (protected with DocShield credentials)