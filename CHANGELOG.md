# Changelog

All notable changes to FastAPI DocShield will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-05-07

### Added
- Initial release of FastAPI DocShield
- Core implementation of DocShield for securing FastAPI docs with HTTP Basic Auth
- Support for protecting /docs (Swagger UI), /redoc, and /openapi.json endpoints
- Customizable endpoint URLs
- Support for multiple valid username/password combinations
- Custom UI resources for Swagger UI and ReDoc
- Comprehensive test suite with unit and integration tests
- Support for all Python versions from 3.7 to 3.13
- Full compatibility with uv package manager
- GitHub Actions workflow for testing across Python versions
- Example applications showcasing basic and advanced usage
- Interactive demo script for easy testing
- Detailed documentation with installation and usage instructions