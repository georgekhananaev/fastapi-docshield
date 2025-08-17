"""
Test script for DocShield CDN fallback feature.

This script demonstrates the different modes of DocShield:
1. Default mode with CDN fallback
2. Prefer local mode
3. CDN only mode (no fallback)
"""

import uvicorn
from fastapi import FastAPI

# Import from local development version
from fastapi_docshield import DocShield

def test_cdn_with_fallback():
    """Test default mode - CDN with automatic fallback to local files."""
    app = FastAPI(
        title="DocShield CDN Fallback Test",
        description="Testing automatic fallback when CDN is unavailable",
        version="1.0.0"
    )
    
    @app.get("/")
    def read_root():
        return {
            "mode": "CDN with fallback",
            "description": "Will use CDN first, fallback to local if CDN fails"
        }
    
    @app.get("/test")
    def test_endpoint():
        return {"test": "data"}
    
    # Apply DocShield with CDN fallback (default)
    DocShield(
        app=app,
        credentials={
            "admin": "test123",
            "dev": "dev456"
        },
        use_cdn_fallback=True,  # This is default, shown for clarity
        prefer_local=False      # This is default, shown for clarity
    )
    
    print("=" * 70)
    print("DocShield CDN Fallback Test")
    print("=" * 70)
    print("Mode: CDN with automatic fallback")
    print("Access documentation at: http://localhost:8001/docs")
    print("Credentials: admin/test123 or dev/dev456")
    print()
    print("Open browser console to see fallback in action if CDN fails")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)

def test_prefer_local():
    """Test prefer local mode - Always use local files."""
    app = FastAPI(
        title="DocShield Local Mode Test",
        description="Testing local static files preference",
        version="1.0.0"
    )
    
    @app.get("/")
    def read_root():
        return {
            "mode": "Prefer local",
            "description": "Always uses local static files"
        }
    
    # Apply DocShield preferring local files
    DocShield(
        app=app,
        credentials={"admin": "test123"},
        prefer_local=True  # Prefer local files over CDN
    )
    
    print("=" * 70)
    print("DocShield Local Mode Test")
    print("=" * 70)
    print("Mode: Prefer local static files")
    print("Access documentation at: http://localhost:8002/docs")
    print("Credentials: admin/test123")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8002)

def test_cdn_only():
    """Test CDN only mode - No fallback."""
    app = FastAPI(
        title="DocShield CDN Only Test",
        description="Testing CDN without fallback",
        version="1.0.0"
    )
    
    @app.get("/")
    def read_root():
        return {
            "mode": "CDN only",
            "description": "Uses CDN without fallback"
        }
    
    # Apply DocShield with CDN only (no fallback)
    DocShield(
        app=app,
        credentials={"admin": "test123"},
        use_cdn_fallback=False,  # Disable fallback
        prefer_local=False        # Don't use local
    )
    
    print("=" * 70)
    print("DocShield CDN Only Test")
    print("=" * 70)
    print("Mode: CDN only (no fallback)")
    print("Access documentation at: http://localhost:8003/docs")
    print("Credentials: admin/test123")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8003)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "fallback":
            test_cdn_with_fallback()
        elif mode == "local":
            test_prefer_local()
        elif mode == "cdn":
            test_cdn_only()
        else:
            print("Usage: python test_fallback.py [fallback|local|cdn]")
    else:
        # Default to testing CDN with fallback
        test_cdn_with_fallback()