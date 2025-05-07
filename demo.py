"""
DocShield Demo Script

This script runs a simple FastAPI application with DocShield protection
on documentation endpoints. Use it to quickly verify that DocShield is
working correctly.

To run the demo:
    python demo.py

Then access:
    http://localhost:8000/docs
    http://localhost:8000/redoc

When prompted for credentials, use:
    Username: admin
    Password: password123
    
    or
    
    Username: user
    Password: user456
"""
import uvicorn
from fastapi import FastAPI
from fastapi_docshield import DocShield

def main():
    # Create a FastAPI app
    app = FastAPI(
        title="DocShield Demo API",
        description="A demonstration of DocShield for protecting FastAPI documentation",
        version="1.0.0"
    )
    
    # Add some API routes
    @app.get("/")
    def read_root():
        """Return a welcome message."""
        return {
            "message": "Welcome to DocShield Demo API",
            "docs": "Visit /docs or /redoc (protected with authentication)"
        }
    
    @app.get("/users")
    def get_users():
        """Get a list of sample users."""
        return [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
        ]
    
    @app.get("/users/{user_id}")
    def get_user(user_id: int):
        """Get a specific user by ID."""
        return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}
    
    # Apply DocShield to protect documentation
    DocShield(
        app=app,
        credentials={
            "admin": "password123",
            "user": "user456"
        }
    )
    
    # Display information
    print("=" * 70)
    print("DocShield Demo Server")
    print("=" * 70)
    print("API running at: http://localhost:8000")
    print()
    print("Documentation URLs (protected with HTTP Basic Auth):")
    print("- Swagger UI: http://localhost:8000/docs")
    print("- ReDoc:      http://localhost:8000/redoc")
    print()
    print("Authentication credentials:")
    print("- Username: admin, Password: password123")
    print("- Username: user,  Password: user456")
    print("=" * 70)
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()