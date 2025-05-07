# FastAPI DocShield

A simple FastAPI integration to protect documentation endpoints with HTTP Basic Authentication.

[![PyPI version](https://badge.fury.io/py/fastapi-docshield.svg)](https://badge.fury.io/py/fastapi-docshield)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/georgekhananaev/fastapi-docshield)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Tests Status](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/georgekhananaev/fastapi-docshield)
[![UV Compatible](https://img.shields.io/badge/uv-compatible-blueviolet)](https://github.com/astral-sh/uv)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/georgekhananaev/fastapi-docshield/graphs/commit-activity)

## Features

- Protect FastAPI's `/docs` (Swagger UI) and `/redoc` endpoints with HTTP Basic Authentication
- Simple integration with minimal code
- Customizable endpoint URLs
- Support for custom Swagger UI and ReDoc JavaScript/CSS URLs
- Support for multiple valid username/password combinations

## Installation

### From PyPI (Recommended)

```bash
# Install with pip
pip install fastapi-docshield

# Or install with uv (recommended for faster installation)
uv pip install fastapi-docshield
```

### From Source

You can also install the package directly from the source code:

```bash
# Clone the repository
git clone https://github.com/georgekhananaev/fastapi-docshield.git
cd fastapi-docshield

# Install in development mode using pip
pip install -e .

# Or using uv (recommended for faster installation)
uv pip install -e .
```

### Using uv (Recommended)

This package is fully compatible with [uv](https://github.com/astral-sh/uv), the ultra-fast Python package installer and resolver. Using uv can significantly speed up dependency installation and provide a more reliable development environment:

```bash
# Install with uv
uv pip install -e .

# Install with test dependencies
uv pip install -e ".[dev]"
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()

# Your regular FastAPI routes
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Initialize DocShield with your credentials
DocShield(
    app=app,
    credentials={
        "admin": "password123",
        "developer": "dev456"
    }
)

# That's it! Your docs are now protected
```

## Running Examples

The repository includes several example applications that you can run to see DocShield in action:

### Basic Example

```bash
# Navigate to the project directory
cd fastapi-docshield

# Run the basic example
uvicorn examples.basic_example:app --reload
```

Then visit:
- http://localhost:8000/docs (will prompt for credentials)
- Username: `admin`, Password: `password123`
- Or Username: `developer`, Password: `dev456`

### Advanced Example

```bash
# Run the advanced example
uvicorn examples.advanced_example:app --reload
```

Then visit:
- http://localhost:8000/api/docs (with custom URLs)
- Username: `admin`, Password: `admin123`

### Quick Demo

```bash
# Run the demo script
python demo.py
```

This will start a demo server with protected documentation endpoints. Visit http://localhost:8000/docs and use:
- Username: `admin`, Password: `password123`
- OR Username: `user`, Password: `user456`

## Advanced Usage

### Custom URLs

You can customize the URLs for your documentation endpoints:

```python
DocShield(
    app=app,
    credentials={"admin": "password123"},
    docs_url="/protected-docs",     # Default: /docs
    redoc_url="/protected-redoc",   # Default: /redoc
    openapi_url="/protected-openapi.json"  # Default: /openapi.json
)
```

### Custom UI Resources

You can use custom versions of Swagger UI and ReDoc:

```python
DocShield(
    app=app,
    credentials={"admin": "password123"},
    swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
    swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
)
```

### Multiple Credentials

You can provide multiple valid username/password combinations:

```python
DocShield(
    app=app,
    credentials={
        "admin": "admin_password",
        "developer": "dev_password",
        "viewer": "view_password"
    }
)
```

## Development

### Testing

DocShield is thoroughly tested across multiple Python versions (3.7-3.13) and has a comprehensive test suite. All tests are passing on the latest version.

```bash
# Install test dependencies
pip install pytest httpx
# Or with uv (recommended)
uv pip install pytest httpx

# Run all tests
pytest

# Run specific test file
pytest tests/test_docshield.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=fastapi_docshield
```

#### Supported Python Versions

DocShield has been tested and confirmed working on:
- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

This ensures wide compatibility across projects with different Python version requirements.

### uv Compatibility

FastAPI DocShield is fully compatible with [uv](https://github.com/astral-sh/uv), the ultra-fast Python package installer and resolver. Using uv offers several advantages:

- **Speed**: Install dependencies significantly faster
- **Reliability**: More reliable dependency resolution
- **Reproducibility**: Better dependency lockfiles with `uv.lock`
- **Modern tooling**: Integration with modern Python development workflows

All tests and examples have been verified to work with uv. The project includes a `uv.lock` file for reproducible installations.

## Troubleshooting

### Authentication Not Working

If the authentication isn't working:

1. Make sure you're using a browser that supports HTTP Basic Authentication
2. Try using incognito/private mode if the browser is caching credentials
3. Verify that the credentials you're using match exactly what you provided in the code
4. Check that there are no conflicting routes in your FastAPI app

### Testing with cURL

You can test the authentication with cURL:

```bash
# Without credentials (should return 401)
curl -i http://localhost:8000/docs

# With credentials (should return 200)
curl -i -u admin:password123 http://localhost:8000/docs
```

## Security Notes

- HTTP Basic Authentication sends credentials in base64 encoding, which is NOT secure over HTTP
- Always use HTTPS in production to protect credentials
- Consider using more robust authentication methods for production APIs
- DocShield is designed to protect documentation only, not your API endpoints

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information.

## Changelog

For a detailed history of changes, please see the [CHANGELOG.md](CHANGELOG.md) file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**George Khananaev** - [GitHub Profile](https://github.com/georgekhananaev)