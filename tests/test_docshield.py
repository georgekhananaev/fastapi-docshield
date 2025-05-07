import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_docshield import DocShield
import base64


def get_auth_header(username, password):
    """Create HTTP Basic Auth header for testing."""
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def test_docs_protected():
    """Test that docs endpoint requires authentication"""
    app = FastAPI()
    # Create app with docs enabled
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    shield = DocShield(app=app, credentials={"admin": "password123"})
    
    print(f"In test: app.docs_url = {app.docs_url}")
    print(f"In test: app.redoc_url = {app.redoc_url}")
    print(f"In test: shield.docs_url = {shield.docs_url}")
    
    client = TestClient(app)
    # Request without auth should fail
    response = client.get("/docs")
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text: {response.text[:100]}")  # Just the first 100 chars
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Basic"


def test_redoc_protected():
    """Test that redoc endpoint requires authentication"""
    app = FastAPI()
    # Create app with docs enabled
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    shield = DocShield(app=app, credentials={"admin": "password123"})
    
    client = TestClient(app)
    # Request without auth should fail
    response = client.get("/redoc")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_openapi_protected():
    """Test that openapi.json endpoint requires authentication"""
    app = FastAPI()
    # Create app with docs enabled
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    shield = DocShield(app=app, credentials={"admin": "password123"})
    
    client = TestClient(app)
    # Request without auth should fail
    response = client.get("/openapi.json")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_valid_credentials():
    """Test that valid credentials allow access to docs endpoints"""
    app = FastAPI()
    # Create app with docs enabled
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    shield = DocShield(app=app, credentials={"admin": "password123"})
    
    client = TestClient(app)
    # Use auth headers directly
    headers = get_auth_header("admin", "password123")
    
    response = client.get("/docs", headers=headers)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    response = client.get("/openapi.json", headers=headers)
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


def test_invalid_credentials():
    """Test that invalid credentials are rejected"""
    app = FastAPI()
    # Create app with docs enabled
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    shield = DocShield(app=app, credentials={"admin": "password123"})
    
    client = TestClient(app)
    # Use incorrect password in auth headers
    headers = get_auth_header("admin", "wrongpassword")
    response = client.get("/docs", headers=headers)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_multiple_credentials():
    """Test that multiple valid credentials work"""
    app = FastAPI()
    # Create app with docs enabled
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    shield = DocShield(app=app, credentials={
        "admin": "password123", 
        "dev": "devpass"
    })
    
    client = TestClient(app)
    
    # Test first credential pair
    headers1 = get_auth_header("admin", "password123")
    response = client.get("/docs", headers=headers1)
    assert response.status_code == 200
    
    # Test second credential pair
    headers2 = get_auth_header("dev", "devpass")
    response = client.get("/docs", headers=headers2)
    assert response.status_code == 200


def test_custom_urls():
    """Test that custom URLs work as expected"""
    app = FastAPI()
    # Create app with docs enabled
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    # We need to add a simple route to initialize FastAPI
    @app.get("/")
    def read_root():
        return {"message": "Hello World"}
    
    shield = DocShield(
        app=app,
        credentials={"admin": "password123"},
        docs_url="/custom-docs",
        redoc_url="/custom-redoc",
        openapi_url="/custom-openapi.json"
    )
    
    client = TestClient(app)
    headers = get_auth_header("admin", "password123")
    
    # Test that original URLs return 404
    with pytest.raises(Exception):
        client.get("/docs")
        
    with pytest.raises(Exception):
        client.get("/redoc")
    
    # Custom URLs should work with auth
    response = client.get("/custom-docs", headers=headers)
    assert response.status_code == 200
    
    response = client.get("/custom-redoc", headers=headers)
    assert response.status_code == 200
    
    response = client.get("/custom-openapi.json", headers=headers)
    assert response.status_code == 200