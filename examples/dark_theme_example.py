"""
Example showing how to use DocShield with fastapi-swagger-dark theme.

This example demonstrates how to integrate DocShield with the 
fastapi-swagger-dark package for a complete dark theme solution.

Run with:
    uvicorn dark_theme_example:app --reload
"""

from fastapi import FastAPI
from fastapi_docshield import DocShield
import requests

# Create FastAPI app
app = FastAPI(
    title="Dark Theme API",
    description="API with dark theme documentation from fastapi-swagger-dark",
    version="1.0.0"
)

# Add some routes
@app.get("/")
def read_root():
    """Return a welcome message."""
    return {"message": "Dark theme API with protected documentation"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """Get an item by ID."""
    return {"item_id": item_id, "q": q}

@app.post("/items/")
def create_item(name: str, price: float):
    """Create a new item."""
    return {"name": name, "price": price}

# Fetch dark theme CSS from fastapi-swagger-dark repository
try:
    dark_theme_response = requests.get(
        "https://raw.githubusercontent.com/georgekhananaev/fastapi-swagger-dark/main/src/fastapi_swagger_dark/swagger_ui_dark.min.css",
        timeout=5
    )
    dark_css = dark_theme_response.text if dark_theme_response.status_code == 200 else None
except:
    dark_css = None
    print("Warning: Could not fetch dark theme CSS, using default theme")

# Custom JavaScript for additional functionality
custom_js = """
// Log when documentation is accessed
console.log('🌙 Dark theme documentation loaded at:', new Date().toISOString());

// Add custom behavior
document.addEventListener('DOMContentLoaded', function() {
    // Add a custom welcome message
    const info = document.querySelector('.info');
    if (info) {
        const banner = document.createElement('div');
        banner.style.cssText = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; text-align: center;';
        banner.innerHTML = '🔒 Protected Documentation with Dark Theme';
        info.insertBefore(banner, info.firstChild);
    }
    
    // Log API operations when clicked
    document.addEventListener('click', function(e) {
        if (e.target.closest('.opblock-summary')) {
            const operation = e.target.closest('.opblock');
            const method = operation.className.match(/opblock-(\\w+)/)[1];
            const path = operation.querySelector('.opblock-summary-path').textContent;
            console.log(`📍 Viewing: ${method.toUpperCase()} ${path}`);
        }
    });
});
"""

# Apply DocShield with dark theme
DocShield(
    app=app,
    credentials={
        "admin": "darkadmin",
        "developer": "darkdev"
    },
    
    # Use CDN with fallback for reliability
    use_cdn_fallback=True,
    
    # Apply dark theme CSS if available
    custom_css=dark_css if dark_css else "",
    
    # Add custom JavaScript
    custom_js=custom_js
)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🌙 Dark Theme API with DocShield")
    print("=" * 70)
    print("Server running at: http://localhost:8000")
    print("Documentation at: http://localhost:8000/docs")
    print("ReDoc at: http://localhost:8000/redoc")
    print()
    print("Credentials:")
    print("  Username: admin, Password: darkadmin")
    print("  Username: developer, Password: darkdev")
    print()
    if dark_css:
        print("✅ Dark theme CSS loaded successfully")
    else:
        print("⚠️  Using default theme (dark theme CSS not loaded)")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)