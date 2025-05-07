# FastAPI DocShield

A simple FastAPI integration to protect documentation endpoints with HTTP Basic Authentication.

## Features

- Protect FastAPI's `/docs` (Swagger UI) and `/redoc` endpoints with HTTP Basic Authentication
- Simple integration with minimal code
- Customizable endpoint URLs
- Support for custom Swagger UI and ReDoc JavaScript/CSS URLs
- Support for multiple valid username/password combinations

## Installation

Since this package is not yet published to PyPI, you need to install it locally:

```bash
# Clone the repository
git clone https://github.com/georgekhananaev/fastapi-docshield.git
cd fastapi-docshield

# Install locally in development mode
pip install -e .

# Or using uv
uv pip install -e .
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

```bash
# Install test dependencies
pip install pytest httpx
# Or with uv
uv pip install pytest httpx

# Run all tests
pytest

# Run specific test file
pytest tests/test_docshield.py

# Run with verbose output
pytest -v
```

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.