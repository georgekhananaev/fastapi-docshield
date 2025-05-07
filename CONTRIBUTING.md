# Contributing to FastAPI DocShield

Thank you for considering contributing to FastAPI DocShield! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/georgekhananaev/fastapi-docshield.git
   cd fastapi-docshield
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   # or
   pip install fastapi pytest pytest-cov httpx
   ```

## Running Tests

To run the tests:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=fastapi_docshield
```

## Code Style

This project uses the following style guides:

- [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style
- [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings

Before submitting a pull request, please make sure your code follows these guidelines.

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation if needed
3. Add tests for new features
4. Create a pull request with a clear description of the changes

## License

By contributing to FastAPI DocShield, you agree that your contributions will be licensed under its MIT License.