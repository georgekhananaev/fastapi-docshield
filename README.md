# FastAPI DocShield

A simple FastAPI integration to protect documentation endpoints with HTTP Basic Authentication.

[![PyPI version](https://badge.fury.io/py/fastapi-docshield.svg)](https://badge.fury.io/py/fastapi-docshield)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/georgekhananaev/fastapi-docshield)
[![Tests Status](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/georgekhananaev/fastapi-docshield)
[![UV Compatible](https://img.shields.io/badge/uv-compatible-blueviolet)](https://github.com/astral-sh/uv)

## About

Protect FastAPI's `/docs`, `/redoc`, and `/openapi.json` endpoints with HTTP Basic Authentication.

## Installation

### From PyPI

```bash
# Install with pip
pip install fastapi-docshield

# Or with uv
uv pip install fastapi-docshield
```

### From Source

```bash
git clone https://github.com/georgekhananaev/fastapi-docshield.git
cd fastapi-docshield
pip install -e .
```

## Quick Usage

### Single User

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Add protection to docs with a single user
DocShield(
    app=app,
    credentials={"admin": "password123"}
)
```

### Multiple Users

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Add protection to docs with multiple users
DocShield(
    app=app,
    credentials={
        "admin": "admin_password",
        "developer": "dev_password",
        "viewer": "viewer_password"
    }
)
```

### CDN Fallback Mode (Default)

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()

# Default mode: Use CDN with automatic fallback to local files
DocShield(
    app=app,
    credentials={"admin": "password123"},
    use_cdn_fallback=True  # Default - automatically falls back to local if CDN fails
)
```

### Prefer Local Files

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()

# Always use local files instead of CDN
DocShield(
    app=app,
    credentials={"admin": "password123"},
    prefer_local=True  # Serve documentation from bundled static files
)
```

### CDN Only (No Fallback)

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()

# Use CDN without fallback (original behavior)
DocShield(
    app=app,
    credentials={"admin": "password123"},
    use_cdn_fallback=False  # Disable fallback, CDN only
)
```

### Custom CSS and JavaScript

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield
import requests

app = FastAPI()

# Load dark theme CSS from external source
# You can use https://github.com/georgekhananaev/fastapi-swagger-dark
dark_theme_url = "https://raw.githubusercontent.com/georgekhananaev/fastapi-swagger-dark/main/src/fastapi_swagger_dark/swagger_ui_dark.min.css"
custom_css = requests.get(dark_theme_url).text

# Custom JavaScript for analytics
custom_js = """
console.log('📊 Documentation accessed at:', new Date().toISOString());
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dark theme loaded!');
});
"""

# Apply with custom styling
DocShield(
    app=app,
    credentials={"admin": "password123"},
    custom_css=custom_css,
    custom_js=custom_js
)
```

#### Using with fastapi-swagger-dark

For a complete dark theme solution, you can use the [fastapi-swagger-dark](https://github.com/georgekhananaev/fastapi-swagger-dark) package:

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield
import requests

app = FastAPI()

# Fetch dark theme CSS
response = requests.get(
    "https://raw.githubusercontent.com/georgekhananaev/fastapi-swagger-dark/main/src/fastapi_swagger_dark/swagger_ui_dark.min.css"
)
dark_css = response.text

DocShield(
    app=app,
    credentials={"admin": "password123"},
    custom_css=dark_css  # Apply dark theme
)
```

See [examples/custom_styling.py](examples/custom_styling.py) for more customization examples including:
- ✨ Minimal clean theme
- 🏢 Corporate theme with analytics
- 📖 ReDoc customization
- 🎨 Custom branding

## Running Demo

```bash
# Run the demo app
python demo.py

# Visit http://localhost:8000/docs
# Username: admin
# Password: password123
```

## Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=fastapi_docshield
```

## Features

- Protect Swagger UI, ReDoc, and OpenAPI JSON endpoints
- Customizable endpoint URLs
- Multiple username/password combinations
- **Automatic CDN fallback** - Falls back to local files if CDN is unavailable
- **Local file preference option** - Serve documentation from local files for better reliability
- **Custom CSS and JavaScript injection** - Fully customize the look and behavior of documentation
- **Resilient documentation** - Works even when CDN is down or blocked
- Tested on Python 3.7-3.13
- Compatible with uv package manager

## Changelog

### Version 0.2.1 (2025-08-17)
- **Fixed**: Blank page issue after authentication for some users
  - Improved handling of custom URL parameters by storing them as instance variables
  - Simplified `_setup_routes()` method for better maintainability
  - Applied fix from PR #2 for more robust URL parameter handling
- **Fixed**: Route removal logic now correctly removes all default documentation routes
  - Properly removes `/docs`, `/redoc`, and `/openapi.json` endpoints
  - Prevents 500 errors when accessing old endpoints
- **Improved**: Example files and documentation
  - Fixed `custom_styling.py` to work with uvicorn by adding default app variable
  - Standardized credentials across all custom styling examples
  - Added `python-multipart` to dev dependencies for form data handling
  - Added clear run instructions in example files

### Version 0.2.0 (2025-08-17)
- **Added**: Custom CSS and JavaScript injection support
  - New `custom_css` parameter to inject custom styles into documentation pages
  - New `custom_js` parameter to inject custom JavaScript for enhanced functionality
  - Complete customization examples for dark theme, minimal theme, corporate branding, and analytics
  - Support for both Swagger UI and ReDoc customization
- **Added**: Automatic CDN fallback to local files for better reliability
  - Documentation now automatically falls back to bundled static files if CDN is unavailable
  - New `prefer_local` option to always serve from local files
  - New `use_cdn_fallback` option to control fallback behavior
  - Bundled Swagger UI and ReDoc static files for offline capability
- **Fixed**: Static file URL bug that caused blank documentation pages
  - Previously, when no custom CDN URLs were provided, the package would pass `None` values to FastAPI's documentation functions
  - This resulted in HTML with `href="None"` and `src="None"`, causing white/blank pages
  - Now properly handles default CDN URLs when custom URLs are not specified

### Version 0.1.0 (2025-01-15)
- Initial release
- Basic HTTP authentication for FastAPI documentation endpoints
- Support for multiple users

## License

MIT License - Copyright (c) 2025 George Khananaev