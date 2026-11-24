# FastAPI DocShield

Protect FastAPI's `/docs`, `/redoc` and `/openapi.json` with a login: HTTP Basic Authentication or a login page.

[![PyPI version](https://img.shields.io/pypi/v/fastapi-docshield)](https://pypi.org/project/fastapi-docshield/)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-docshield)](https://pypi.org/project/fastapi-docshield/)
[![Tests](https://github.com/georgekhananaev/fastapi-docshield/actions/workflows/python-tests.yml/badge.svg)](https://github.com/georgekhananaev/fastapi-docshield/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Protects Swagger UI, ReDoc and the OpenAPI JSON with one call
- HTTP Basic Authentication, or a login page with a session and a "Log out" link
- Several users, and different documentation for different users
- Works without the CDN: Swagger UI and ReDoc are bundled as a fallback
- Custom CSS and JavaScript for the documentation pages
- Custom URLs for every endpoint, and support for apps behind a proxy
- No dependencies besides FastAPI

## Installation

```bash
pip install fastapi-docshield

# Or with uv
uv add fastapi-docshield
```

## Quick start

```python
from fastapi import FastAPI
from fastapi_docshield import DocShield

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


DocShield(
    app=app,
    credentials={
        "admin": "admin_password",
        "developer": "dev_password",
    },
)
```

Call `DocShield` after you create the app. `/docs`, `/redoc` and `/openapi.json` now ask for one of the usernames and passwords. In a real app, read the passwords from environment variables or your settings, not from the source code.

## Login page with logout

HTTP Basic Authentication has no logout: the browser keeps sending the password until it is closed. If you want a login page and a "Log out" link, use form login:

```python
DocShield(
    app=app,
    credentials={"admin": "admin_password"},
    auth_method="form",
)
```

A visitor who opens `/docs` is sent to a login page. After login the session lives in a signed, HTTP-only cookie for 8 hours (`session_max_age`, in seconds). The documentation pages get a "Log out" link in the bottom right corner; hide it with `custom_css=".docshield-logout { display: none; }"` if you link to the logout URL yourself.

Good to know:

- Scripts can still send HTTP Basic credentials, for example `curl -u admin:admin_password https://example.com/openapi.json`.
- The cookie is signed with a random secret that is made when the app starts. That is fine for a single process. If the app runs in several worker processes, or sessions should survive a restart, set `session_secret` to a long random value of your own, for example from an environment variable.
- A session ends when it expires, on logout, and when that user's password changes.
- The login page is at `/docshield/login` and logout at `/docshield/logout`. Change them with `login_url` and `logout_url`.

## Different documentation for different users

`user_tags` maps a username to the route tags that user may see. A user with tags sees only the matching routes, their schemas and tag descriptions. Users that are missing from `user_tags`, or mapped to `None`, see everything.

```python
@app.get("/", tags=["general"])
def read_root():
    return {"Hello": "World"}


@app.post("/posts/{post_id}", tags=["admin"])
def create_post(post_id: int):
    return {"id": post_id}


DocShield(
    app=app,
    credentials={
        "admin": "admin_password",
        "developer": "dev_password",
    },
    user_tags={
        "admin": None,  # Sees all routes and schemas
        "developer": ["general"],  # Sees only routes tagged "general"
    },
)
```

Routes without a tag are hidden from users that have a tag list.

This only changes what the documentation shows. It doesn't stop anyone from calling a hidden route, so the routes still need their own checks.

## Working without the CDN

By default the pages load Swagger UI and ReDoc from the jsDelivr CDN and switch to the copies bundled in the package when the CDN can't be reached.

```python
# Always use the bundled files, never the CDN
DocShield(app=app, credentials=credentials, prefer_local=True)

# CDN only, without the bundled fallback
DocShield(app=app, credentials=credentials, use_cdn_fallback=False)

# Your own copies
DocShield(
    app=app,
    credentials=credentials,
    swagger_js_url="https://assets.example.com/swagger-ui-bundle.js",
    swagger_css_url="https://assets.example.com/swagger-ui.css",
    redoc_js_url="https://assets.example.com/redoc.standalone.js",
)
```

## Custom CSS and JavaScript

```python
from pathlib import Path

DocShield(
    app=app,
    credentials={"admin": "admin_password"},
    custom_css=Path("static/swagger_ui_dark.min.css").read_text(encoding="utf-8"),
    custom_js="console.log('Documentation opened at', new Date().toISOString());",
)
```

The CSS is added after the Swagger UI stylesheet, so your rules win. The JavaScript runs after the documentation has loaded; on the Swagger UI page the `ui` object is available to it.

A ready-made dark theme is in [fastapi-swagger-ui-dark-theme](https://github.com/georgekhananaev/fastapi-swagger-ui-dark-theme). See [examples/custom_styling.py](examples/custom_styling.py) for more themes: a minimal one, a corporate one with analytics, and a ReDoc one.

## All options

| Option | Default | What it does |
| --- | --- | --- |
| `app` | required | The FastAPI app to protect |
| `credentials` | required | Dictionary of username to password |
| `docs_url` | `"/docs"` | Path of the Swagger UI page |
| `redoc_url` | `"/redoc"` | Path of the ReDoc page |
| `openapi_url` | `"/openapi.json"` | Path of the OpenAPI schema |
| `swagger_js_url`, `swagger_css_url`, `redoc_js_url` | `None` | Your own URLs for the Swagger UI and ReDoc files |
| `use_cdn_fallback` | `True` | Fall back to the bundled files when the CDN fails |
| `prefer_local` | `False` | Always use the bundled files |
| `custom_css`, `custom_js` | `None` | CSS and JavaScript to add to the documentation pages |
| `user_tags` | `None` | Username to allowed route tags |
| `auth_method` | `"basic"` | `"basic"` or `"form"` |
| `login_url`, `logout_url` | `"/docshield/login"`, `"/docshield/logout"` | Paths of the login page and the logout URL (form login) |
| `session_secret` | `None` | Secret for signing the session cookie; needed with several worker processes (form login) |
| `session_max_age` | `28800` | Lifetime of a session in seconds (form login) |

DocShield follows the app's own settings where they exist: a page that is switched off on the app (`FastAPI(docs_url=None)`) stays off, `swagger_ui_parameters` and `swagger_ui_init_oauth` are passed on to Swagger UI, and behind a proxy the root path is put in front of every URL.

## Security notes

- Always serve the documentation over HTTPS. Both HTTP Basic credentials and the session cookie can be read on a plain HTTP connection.
- DocShield keeps casual visitors out of your documentation. It has no rate limiting or lockout, so use long random passwords.
- Passwords are compared in constant time, and the session cookie is signed with HMAC-SHA256.

## Compatibility

- Python 3.8 to 3.14
- FastAPI 0.68 and newer

Every release is tested against the oldest and the newest supported versions.

## Examples

```bash
pip install uvicorn
uvicorn examples.basic_example:app --reload
```

Then open http://localhost:8000/docs and log in with `admin` / `password123`. The [examples](examples) folder also has [form login](examples/form_login.py), [user tags](examples/user_tags.py) and [custom styling](examples/custom_styling.py).

## Development

```bash
git clone https://github.com/georgekhananaev/fastapi-docshield.git
cd fastapi-docshield
pip install -e ".[dev]"

pytest --cov=fastapi_docshield
ruff check . && ruff format --check .
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT License - Copyright (c) 2025 George Khananaev
