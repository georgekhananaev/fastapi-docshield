"""
Examples of using custom CSS and JavaScript with DocShield.

This module demonstrates various ways to customize the appearance
and behavior of your protected documentation pages.

How to run:
-----------
1. With uvicorn (default dark theme):
   uvicorn custom_styling:app --reload

2. Run specific themes directly:
   python custom_styling.py dark      # Dark theme with gradient
   python custom_styling.py minimal   # Clean minimal theme  
   python custom_styling.py corporate # Corporate theme with analytics
   python custom_styling.py redoc     # ReDoc customization

Credentials for all examples:
   Username: demo
   Password: style123

Author: George Khananaev
"""

import uvicorn
from fastapi import FastAPI
from fastapi_docshield import DocShield

# Example 1: Dark Theme with Custom Branding
def dark_theme_example():
    """Example with dark theme and custom branding."""
    app = FastAPI(
        title="Dark Theme API",
        description="API with custom dark theme documentation",
        version="1.0.0"
    )
    
    @app.get("/")
    def root():
        return {"theme": "dark"}
    
    custom_css = """
    /* Dark theme customization */
    .swagger-ui {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .swagger-ui .topbar {
        background-color: #1a1a2e;
        border-bottom: 2px solid #764ba2;
    }
    
    .swagger-ui .topbar .download-url-wrapper {
        display: none;
    }
    
    /* Custom color scheme */
    .swagger-ui .btn.authorize {
        background-color: #764ba2;
        border-color: #764ba2;
    }
    
    .swagger-ui .btn.authorize:hover {
        background-color: #667eea;
        border-color: #667eea;
    }
    
    /* Add company logo */
    .swagger-ui .topbar-wrapper img {
        content: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjMwIiB2aWV3Qm94PSIwIDAgMTAwIDMwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjx0ZXh0IHg9IjUwIiB5PSIyMCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE4IiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPk15IEFQSTwvdGV4dD48L3N2Zz4=');
    }
    
    /* Customize operation blocks */
    .swagger-ui .opblock.opblock-get .opblock-summary {
        border-color: #667eea;
    }
    
    .swagger-ui .opblock.opblock-post .opblock-summary {
        border-color: #764ba2;
    }
    """
    
    custom_js = """
    // Add custom welcome message
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🎨 Custom Dark Theme Loaded!');
        
        // Add custom header
        const topbar = document.querySelector('.topbar-wrapper');
        if (topbar) {
            const customHeader = document.createElement('div');
            customHeader.style.color = 'white';
            customHeader.style.padding = '10px';
            customHeader.style.fontSize = '14px';
            customHeader.innerHTML = '🔒 Protected Documentation - Authorized Access Only';
            topbar.appendChild(customHeader);
        }
    });
    """
    
    DocShield(
        app=app,
        credentials={"demo": "style123"},
        custom_css=custom_css,
        custom_js=custom_js
    )
    
    print("=" * 70)
    print("Dark Theme Example")
    print("Access at: http://localhost:8000/docs")
    print("Credentials: demo/style123")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Example 2: Minimal Clean Theme
def minimal_theme_example():
    """Example with minimal, clean theme."""
    app = FastAPI(
        title="Minimal API",
        description="Clean and minimal documentation style",
        version="1.0.0"
    )
    
    @app.get("/users")
    def get_users():
        return [{"id": 1, "name": "John"}]
    
    custom_css = """
    /* Minimal clean theme */
    .swagger-ui .wrapper {
        max-width: 960px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .swagger-ui .topbar {
        display: none;
    }
    
    .swagger-ui .info {
        margin-bottom: 50px;
        padding: 30px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    
    .swagger-ui .info .title {
        font-family: 'Georgia', serif;
        color: #2c3e50;
    }
    
    .swagger-ui .scheme-container {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .swagger-ui .opblock {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .swagger-ui .opblock-summary {
        border: none;
    }
    
    /* Softer colors */
    .swagger-ui .opblock.opblock-get .opblock-summary {
        background: rgba(97, 175, 254, 0.1);
    }
    
    .swagger-ui .opblock.opblock-post .opblock-summary {
        background: rgba(73, 204, 144, 0.1);
    }
    
    .swagger-ui .opblock.opblock-put .opblock-summary {
        background: rgba(252, 161, 48, 0.1);
    }
    
    .swagger-ui .opblock.opblock-delete .opblock-summary {
        background: rgba(249, 62, 62, 0.1);
    }
    """
    
    custom_js = """
    // Add subtle animations
    document.addEventListener('DOMContentLoaded', function() {
        // Add fade-in animation to operation blocks
        const opblocks = document.querySelectorAll('.opblock');
        opblocks.forEach((block, index) => {
            block.style.opacity = '0';
            block.style.transform = 'translateY(20px)';
            block.style.transition = 'opacity 0.5s, transform 0.5s';
            
            setTimeout(() => {
                block.style.opacity = '1';
                block.style.transform = 'translateY(0)';
            }, index * 100);
        });
        
        // Add custom footer
        const wrapper = document.querySelector('.swagger-ui');
        if (wrapper) {
            const footer = document.createElement('div');
            footer.style.textAlign = 'center';
            footer.style.padding = '40px';
            footer.style.color = '#6c757d';
            footer.style.fontSize = '14px';
            footer.innerHTML = '© 2025 Minimal API - Built with ❤️ and DocShield';
            wrapper.appendChild(footer);
        }
    });
    """
    
    DocShield(
        app=app,
        credentials={"demo": "style123"},
        custom_css=custom_css,
        custom_js=custom_js
    )
    
    print("=" * 70)
    print("Minimal Theme Example")
    print("Access at: http://localhost:8001/docs")
    print("Credentials: demo/style123")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)


# Example 3: Corporate Theme with Analytics
def corporate_theme_example():
    """Example with corporate theme and usage analytics."""
    app = FastAPI(
        title="Corporate API",
        description="Enterprise-grade API with corporate branding",
        version="2.0.0"
    )
    
    @app.get("/analytics")
    def get_analytics():
        return {"status": "tracking"}
    
    custom_css = """
    /* Corporate theme */
    :root {
        --corporate-primary: #003366;
        --corporate-secondary: #0066cc;
        --corporate-accent: #ff6600;
    }
    
    .swagger-ui {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .swagger-ui .topbar {
        background-color: var(--corporate-primary);
        padding: 15px;
    }
    
    .swagger-ui .topbar .topbar-wrapper::before {
        content: 'ACME CORP';
        color: white;
        font-size: 20px;
        font-weight: bold;
        margin-right: 20px;
    }
    
    /* Add security badge */
    .swagger-ui .info::before {
        content: '🔐 ENTERPRISE SECURITY ENABLED';
        display: block;
        background: var(--corporate-accent);
        color: white;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    
    /* Corporate button styles */
    .swagger-ui .btn {
        border-radius: 2px;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .swagger-ui .btn.authorize {
        background-color: var(--corporate-secondary);
        border-color: var(--corporate-secondary);
    }
    
    .swagger-ui .btn.authorize.locked {
        background-color: var(--corporate-accent);
        border-color: var(--corporate-accent);
    }
    
    /* Professional operation blocks */
    .swagger-ui .opblock {
        border-left: 4px solid var(--corporate-primary);
        border-radius: 0;
    }
    
    .swagger-ui .opblock-summary {
        font-weight: 500;
    }
    
    /* Add version banner */
    .swagger-ui .info .title::after {
        content: ' | Enterprise Edition';
        color: var(--corporate-accent);
        font-size: 14px;
    }
    """
    
    custom_js = """
    // Corporate analytics and features
    (function() {
        // Track API documentation usage
        let startTime = Date.now();
        let clickCount = 0;
        
        // Log page view
        console.log('📊 API Documentation accessed at:', new Date().toISOString());
        
        // Track operation clicks
        document.addEventListener('click', function(e) {
            if (e.target.closest('.opblock-summary')) {
                clickCount++;
                const operation = e.target.closest('.opblock');
                const method = operation.className.match(/opblock-(\\w+)/)[1];
                const path = operation.querySelector('.opblock-summary-path').textContent;
                
                console.log(`📈 Operation viewed: ${method.toUpperCase()} ${path}`);
                
                // Show usage hint after 3 clicks
                if (clickCount === 3) {
                    const hint = document.createElement('div');
                    hint.style.cssText = 'position:fixed;top:20px;right:20px;background:#ff6600;color:white;padding:15px;border-radius:4px;z-index:9999;';
                    hint.innerHTML = '💡 Tip: Use Ctrl+F to search endpoints';
                    document.body.appendChild(hint);
                    setTimeout(() => hint.remove(), 5000);
                }
            }
        });
        
        // Add session timer
        setInterval(function() {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            console.log(`⏱️ Session duration: ${minutes}:${seconds.toString().padStart(2, '0')}`);
        }, 60000); // Log every minute
        
        // Add compliance notice
        window.addEventListener('load', function() {
            const notice = document.createElement('div');
            notice.style.cssText = 'background:#003366;color:white;padding:10px;text-align:center;position:fixed;bottom:0;left:0;right:0;z-index:9999;font-size:12px;';
            notice.innerHTML = '⚖️ This API is compliant with ISO 27001 and GDPR regulations | 📝 All access is logged for security purposes';
            document.body.appendChild(notice);
        });
        
        // Warn before leaving
        window.addEventListener('beforeunload', function() {
            const duration = Math.floor((Date.now() - startTime) / 1000);
            console.log(`📊 Session ended. Duration: ${duration} seconds, Operations viewed: ${clickCount}`);
        });
    })();
    """
    
    DocShield(
        app=app,
        credentials={"demo": "style123"},
        custom_css=custom_css,
        custom_js=custom_js
    )
    
    print("=" * 70)
    print("Corporate Theme Example")
    print("Access at: http://localhost:8002/docs")
    print("Credentials: demo/style123")
    print("Features: Usage analytics, corporate branding, compliance notices")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8002)


# Example 4: ReDoc Customization
def redoc_custom_example():
    """Example showing ReDoc customization."""
    app = FastAPI(
        title="ReDoc Custom API",
        description="API with customized ReDoc documentation",
        version="1.0.0"
    )
    
    @app.get("/items/{item_id}")
    def get_item(item_id: int):
        return {"item_id": item_id}
    
    custom_css = """
    /* ReDoc customization */
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Custom header */
    .api-info h1::before {
        content: '🚀 ';
    }
    
    /* Custom color scheme */
    [data-section-id] {
        scroll-margin-top: 100px;
    }
    
    .api-content {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Add banner */
    body::before {
        content: '📚 Interactive API Documentation powered by DocShield';
        display: block;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        color: white;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    
    /* Customize menu */
    .menu-content {
        background: #f5f5f5;
    }
    
    .menu-content .menu-item-header {
        font-weight: 600;
    }
    
    .menu-content .menu-item-header:hover {
        background: #e0e0e0;
    }
    """
    
    custom_js = """
    // ReDoc customizations
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📖 ReDoc Custom Theme Loaded');
        
        // Add reading progress indicator
        const progressBar = document.createElement('div');
        progressBar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:#2196F3;z-index:10000;transition:width 0.3s;';
        progressBar.style.width = '0%';
        document.body.appendChild(progressBar);
        
        window.addEventListener('scroll', function() {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + '%';
        });
        
        // Add copy buttons to code blocks
        setTimeout(function() {
            const codeBlocks = document.querySelectorAll('pre');
            codeBlocks.forEach(block => {
                const button = document.createElement('button');
                button.textContent = '📋 Copy';
                button.style.cssText = 'position:absolute;top:5px;right:5px;padding:5px 10px;background:#2196F3;color:white;border:none;border-radius:3px;cursor:pointer;font-size:12px;';
                button.onclick = function() {
                    navigator.clipboard.writeText(block.textContent);
                    button.textContent = '✅ Copied!';
                    setTimeout(() => button.textContent = '📋 Copy', 2000);
                };
                block.style.position = 'relative';
                block.appendChild(button);
            });
        }, 1000);
    });
    """
    
    DocShield(
        app=app,
        credentials={"demo": "style123"},
        custom_css=custom_css,
        custom_js=custom_js,
        prefer_local=True  # Use local files for faster loading
    )
    
    print("=" * 70)
    print("ReDoc Custom Example")
    print("Access at: http://localhost:8003/redoc")
    print("Credentials: demo/style123")
    print("Features: Reading progress, copy buttons, custom styling")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8003)


# Create a default app for uvicorn
# This will be used when running: uvicorn custom_styling:app
app = FastAPI(
    title="Custom Styling Examples",
    description="Examples of DocShield with custom CSS and JavaScript",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "DocShield Custom Styling Examples",
        "examples": [
            "python custom_styling.py dark",
            "python custom_styling.py minimal", 
            "python custom_styling.py corporate",
            "python custom_styling.py redoc"
        ]
    }

@app.get("/examples")
def list_examples():
    return {
        "dark": "Dark theme with gradient backgrounds",
        "minimal": "Clean minimal theme",
        "corporate": "Corporate theme with analytics",
        "redoc": "ReDoc customization example"
    }

# Apply dark theme by default to the app
custom_css = """
/* Dark theme customization */
.swagger-ui {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.swagger-ui .topbar {
    background-color: #1a1a2e;
    border-bottom: 2px solid #764ba2;
}

.swagger-ui .btn.authorize {
    background-color: #764ba2;
    border-color: #764ba2;
}
"""

custom_js = """
console.log('🎨 Custom Styling Examples - Default Dark Theme');
document.addEventListener('DOMContentLoaded', function() {
    const info = document.querySelector('.info');
    if (info) {
        const note = document.createElement('div');
        note.style.cssText = 'background:#764ba2;color:white;padding:15px;margin-bottom:20px;border-radius:5px;';
        note.innerHTML = '📝 Note: Run with different themes using: python custom_styling.py [dark|minimal|corporate|redoc]';
        info.insertBefore(note, info.firstChild);
    }
});
"""

DocShield(
    app=app,
    credentials={"demo": "style123"},
    custom_css=custom_css,
    custom_js=custom_js
)

if __name__ == "__main__":
    import sys
    
    examples = {
        "dark": dark_theme_example,
        "minimal": minimal_theme_example,
        "corporate": corporate_theme_example,
        "redoc": redoc_custom_example
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("Available examples:")
        print("  python custom_styling.py dark      - Dark theme with gradient")
        print("  python custom_styling.py minimal   - Clean minimal theme")
        print("  python custom_styling.py corporate - Corporate theme with analytics")
        print("  python custom_styling.py redoc     - ReDoc customization")
        print("\nDefaulting to dark theme...")
        dark_theme_example()