# Publishing to PyPI

This document explains how to publish FastAPI DocShield to PyPI using GitHub Actions.

## Automated Publishing with GitHub Actions

This repository is configured to automatically publish to PyPI whenever a new GitHub Release is created. This is handled by the GitHub Actions workflow defined in `.github/workflows/publish-to-pypi.yml`.

## Requirements

Before you can publish to PyPI, you need to:

1. Create a PyPI account at https://pypi.org/account/register/
2. Generate an API token in your PyPI account settings
3. Add the token as a GitHub repository secret

## Setting up PyPI API Token

1. Log in to your PyPI account
2. Go to Account Settings → API tokens
3. Create a new API token with the scope "Entire account (all projects)"
4. Copy the token (you won't be able to see it again)

## Adding the Token to GitHub Secrets

1. Go to your GitHub repository
2. Click on "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Paste your PyPI API token
6. Click "Add secret"

## Publishing a New Release

To publish a new version to PyPI:

1. Update the version number in `fastapi_docshield/__init__.py` and `pyproject.toml`
2. Add a new section to the CHANGELOG.md describing the changes
3. Commit and push these changes
4. Go to the GitHub repository page
5. Click on "Releases" on the right sidebar
6. Click "Create a new release"
7. Choose a tag version (e.g., `v0.1.0`)
8. Title the release (e.g., "FastAPI DocShield v0.1.0")
9. Add release notes (you can copy from CHANGELOG.md)
10. Click "Publish release"

The GitHub Actions workflow will then:
- Build the package
- Run checks on the package
- Upload the package to PyPI

## Manual Publishing (if needed)

If you need to publish manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the built distribution
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## After Publishing

Once published:
- The package will be available at https://pypi.org/project/fastapi-docshield/
- Users can install it with `pip install fastapi-docshield`
- The PyPI badge in the README will show the latest version

## Troubleshooting

If publishing fails:

1. Check the GitHub Actions logs for detailed error messages
2. Verify that the PyPI API token is correctly set up in GitHub Secrets
3. Ensure the package version in `pyproject.toml` is incremented (PyPI won't allow uploading the same version twice)
4. Make sure the package passes all validation checks with `twine check dist/*`