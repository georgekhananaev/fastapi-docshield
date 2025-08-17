"""
Comprehensive example showcasing all DocShield v0.2.1 features.

This example demonstrates:
- Multiple user credentials
- Custom documentation URLs
- CDN fallback configuration
- Local file preference
- Custom CSS styling
- Custom JavaScript functionality

Run with:
    uvicorn all_features:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi_docshield import DocShield
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Create FastAPI app with comprehensive API
app = FastAPI(
    title="DocShield Feature Showcase",
    description="Demonstrating all features of FastAPI DocShield v0.2.1",
    version="2.0.0"
)

# Define models for the API
class Item(BaseModel):
    """Item model for the API."""
    id: int
    name: str
    price: float
    description: Optional[str] = None
    tags: List[str] = []

class ItemCreate(BaseModel):
    """Model for creating new items."""
    name: str
    price: float
    description: Optional[str] = None
    tags: List[str] = []

# Sample data
items_db = {
    1: Item(id=1, name="Laptop", price=999.99, description="High-performance laptop", tags=["electronics", "computers"]),
    2: Item(id=2, name="Mouse", price=29.99, description="Wireless mouse", tags=["electronics", "accessories"]),
    3: Item(id=3, name="Keyboard", price=79.99, description="Mechanical keyboard", tags=["electronics", "accessories"])
}

# API Routes
@app.get("/", tags=["General"])
def root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to DocShield Feature Showcase API",
        "features": {
            "authentication": "Multiple users supported",
            "cdn_fallback": "Automatic fallback to local files",
            "customization": "Custom CSS and JavaScript injection",
            "urls": "Custom documentation URLs"
        },
        "docs": "/secure/docs",
        "redoc": "/secure/redoc"
    }

@app.get("/items", response_model=List[Item], tags=["Items"])
def list_items(
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(10, description="Number of items to return"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """List all items with optional filtering."""
    items = list(items_db.values())
    
    if tag:
        items = [item for item in items if tag in item.tags]
    
    return items[skip:skip + limit]

@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
def get_item(item_id: int):
    """Get a specific item by ID."""
    if item_id not in items_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.post("/items", response_model=Item, tags=["Items"])
def create_item(item: ItemCreate):
    """Create a new item."""
    new_id = max(items_db.keys()) + 1 if items_db else 1
    new_item = Item(id=new_id, **item.dict())
    items_db[new_id] = new_item
    return new_item

@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
def update_item(item_id: int, item: ItemCreate):
    """Update an existing item."""
    if item_id not in items_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    
    updated_item = Item(id=item_id, **item.dict())
    items_db[item_id] = updated_item
    return updated_item

@app.delete("/items/{item_id}", tags=["Items"])
def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    
    del items_db[item_id]
    return {"message": "Item deleted successfully"}

@app.get("/stats", tags=["Analytics"])
def get_stats():
    """Get API statistics."""
    return {
        "total_items": len(items_db),
        "total_value": sum(item.price for item in items_db.values()),
        "average_price": sum(item.price for item in items_db.values()) / len(items_db) if items_db else 0,
        "timestamp": datetime.now().isoformat()
    }

# Custom CSS for professional styling
custom_css = """
/* Professional styling for documentation */
.swagger-ui .topbar {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 15px;
}

.swagger-ui .topbar .download-url-wrapper {
    display: none;
}

.swagger-ui .topbar-wrapper img {
    display: none;
}

.swagger-ui .topbar-wrapper::after {
    content: '🛡️ DocShield Protected API';
    color: white;
    font-size: 20px;
    font-weight: bold;
}

.swagger-ui .info {
    margin-bottom: 30px;
}

.swagger-ui .info .title {
    color: #1e3c72;
}

.swagger-ui .scheme-container {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    border-left: 4px solid #2a5298;
}

/* Custom styling for operation blocks */
.swagger-ui .opblock.opblock-get {
    border-color: #61affe;
    border-width: 2px;
}

.swagger-ui .opblock.opblock-post {
    border-color: #49cc90;
    border-width: 2px;
}

.swagger-ui .opblock.opblock-put {
    border-color: #fca130;
    border-width: 2px;
}

.swagger-ui .opblock.opblock-delete {
    border-color: #f93e3e;
    border-width: 2px;
}

/* Add animation */
.swagger-ui .opblock {
    transition: all 0.3s ease;
}

.swagger-ui .opblock:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}
"""

# Custom JavaScript for enhanced functionality
custom_js = """
// Enhanced documentation functionality
console.log('🚀 DocShield v0.2.0 - All features enabled');

// Track documentation usage
let operationClicks = 0;
let startTime = Date.now();

document.addEventListener('DOMContentLoaded', function() {
    // Add welcome banner
    const info = document.querySelector('.info');
    if (info) {
        const banner = document.createElement('div');
        banner.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 10px;
            text-align: center;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        banner.innerHTML = `
            <h3 style="margin:0 0 10px 0;">🛡️ Protected Documentation</h3>
            <p style="margin:0;">This API documentation is secured with DocShield v0.2.0</p>
            <small>Features: Multi-user auth | CDN fallback | Custom styling | Enhanced UX</small>
        `;
        info.insertBefore(banner, info.firstChild);
    }
    
    // Add statistics dashboard
    const statsDiv = document.createElement('div');
    statsDiv.id = 'stats-dashboard';
    statsDiv.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: white;
        border: 2px solid #2a5298;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        min-width: 200px;
    `;
    statsDiv.innerHTML = `
        <h4 style="margin:0 0 10px 0; color:#1e3c72;">📊 Session Stats</h4>
        <div id="stats-content">
            <p style="margin:5px 0;">Operations viewed: <span id="op-count">0</span></p>
            <p style="margin:5px 0;">Session time: <span id="session-time">0:00</span></p>
        </div>
    `;
    document.body.appendChild(statsDiv);
    
    // Update session timer
    setInterval(function() {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        document.getElementById('session-time').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
});

// Track operation clicks
document.addEventListener('click', function(e) {
    if (e.target.closest('.opblock-summary')) {
        operationClicks++;
        document.getElementById('op-count').textContent = operationClicks;
        
        const operation = e.target.closest('.opblock');
        const method = operation.className.match(/opblock-(\\w+)/)[1];
        const path = operation.querySelector('.opblock-summary-path').textContent;
        
        console.log(`📍 Operation clicked: ${method.toUpperCase()} ${path}`);
        
        // Show tooltip after 5 clicks
        if (operationClicks === 5) {
            const tooltip = document.createElement('div');
            tooltip.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #2a5298;
                color: white;
                padding: 20px;
                border-radius: 10px;
                z-index: 10000;
                animation: fadeIn 0.5s;
            `;
            tooltip.innerHTML = '💡 Tip: Use Try it out button to test endpoints!';
            document.body.appendChild(tooltip);
            setTimeout(() => tooltip.remove(), 3000);
        }
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+K to focus search
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.operation-filter-input');
        if (searchInput) {
            searchInput.focus();
            console.log('🔍 Search focused');
        }
    }
});

// Log when leaving
window.addEventListener('beforeunload', function() {
    const sessionMinutes = Math.floor((Date.now() - startTime) / 60000);
    console.log(`📊 Session ended: ${sessionMinutes} minutes, ${operationClicks} operations viewed`);
});
"""

# Apply DocShield with all features
DocShield(
    app=app,
    credentials={
        "admin": "admin@2025",      # Admin access
        "developer": "dev@2025",     # Developer access
        "viewer": "view@2025",       # Read-only access
        "tester": "test@2025"        # Tester access
    },
    
    # Custom URLs for documentation
    docs_url="/secure/docs",
    redoc_url="/secure/redoc", 
    openapi_url="/secure/openapi.json",
    
    # CDN with automatic fallback (default: True)
    use_cdn_fallback=True,
    
    # Set to True to always use local files instead of CDN
    prefer_local=False,
    
    # Apply custom styling
    custom_css=custom_css,
    
    # Apply custom JavaScript
    custom_js=custom_js
)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🛡️  DocShield v0.2.1 - All Features Showcase")
    print("=" * 80)
    print()
    print("📍 Server: http://localhost:8000")
    print()
    print("📚 Protected Documentation:")
    print("   • Swagger UI: http://localhost:8000/secure/docs")
    print("   • ReDoc:      http://localhost:8000/secure/redoc")
    print("   • OpenAPI:    http://localhost:8000/secure/openapi.json")
    print()
    print("🔐 Authentication Credentials:")
    print("   • Admin:     admin / admin@2025")
    print("   • Developer: developer / dev@2025")
    print("   • Viewer:    viewer / view@2025")
    print("   • Tester:    tester / test@2025")
    print()
    print("✨ Features Enabled:")
    print("   ✅ Multiple user authentication")
    print("   ✅ Custom documentation URLs")
    print("   ✅ CDN with automatic fallback")
    print("   ✅ Custom CSS styling")
    print("   ✅ Custom JavaScript functionality")
    print("   ✅ Session statistics tracking")
    print("   ✅ Keyboard shortcuts (Ctrl+K for search)")
    print()
    print("=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)