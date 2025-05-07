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

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Add protection to docs
DocShield(
    app=app,
    credentials={"admin": "password123"}
)
```

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
- Tested on Python 3.7-3.13
- Compatible with uv package manager

## License

MIT License - Copyright (c) 2025 George Khananaev