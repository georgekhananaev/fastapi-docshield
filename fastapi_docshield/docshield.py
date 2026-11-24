"""
FastAPI DocShield - protect FastAPI's documentation endpoints with a login.

Author: George Khananaev
License: MIT
Copyright (c) 2025 George Khananaev
"""

import base64
import copy
import hashlib
import hmac
import html
import json
import secrets
import time
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from urllib.parse import parse_qs, quote

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import _templates
from ._version import __version__ as __version__
from .static_handler import (
    REDOC_JS_CDN_URL,
    REDOC_JS_LOCAL_URL,
    STATIC_URL_PREFIX,
    SWAGGER_CSS_CDN_URL,
    SWAGGER_CSS_LOCAL_URL,
    SWAGGER_JS_CDN_URL,
    SWAGGER_JS_LOCAL_URL,
    StaticHandler,
)

AUTH_METHODS = ("basic", "form")
SESSION_COOKIE_NAME = "docshield_session"
NO_STORE = {"Cache-Control": "no-store"}

# The login form sends two short fields, so a bigger body is not a login.
_MAX_LOGIN_BODY = 8 * 1024
_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
_SWAGGER_UI_DEFAULTS: Dict[str, Any] = {
    "dom_id": "#swagger-ui",
    "layout": "BaseLayout",
    "deepLinking": True,
    "showExtensions": True,
    "showCommonExtensions": True,
}


def _root_path(request: Request) -> str:
    """The prefix the app is served under, for example behind a proxy."""
    return request.scope.get("root_path", "").rstrip("/")


def _js(value: Any) -> str:
    """Encode a value as JSON that is safe inside a <script> tag."""
    return json.dumps(value).replace("</", "<\\/")


class DocShield:
    """
    DocShield provides authentication protection for FastAPI's
    built-in documentation endpoints.

    It secures /docs (Swagger UI), /redoc and /openapi.json with
    HTTP Basic Authentication or with a login page.

    Author: George Khananaev
    License: MIT License
    """

    def __init__(
        self,
        app: FastAPI,
        credentials: Dict[str, str],
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        openapi_url: str = "/openapi.json",
        swagger_js_url: Optional[str] = None,
        swagger_css_url: Optional[str] = None,
        redoc_js_url: Optional[str] = None,
        use_cdn_fallback: bool = True,
        prefer_local: bool = False,
        custom_css: Optional[str] = None,
        custom_js: Optional[str] = None,
        user_tags: Optional[Dict[str, Optional[Iterable[str]]]] = None,
        auth_method: str = "basic",
        login_url: str = "/docshield/login",
        logout_url: str = "/docshield/logout",
        session_secret: Union[str, bytes, None] = None,
        session_max_age: int = 8 * 60 * 60,
    ):
        """
        Initialize DocShield with the given FastAPI application and credentials.

        Args:
            app: The FastAPI application instance to protect
            credentials: Dictionary of username:password pairs for authentication
            docs_url: URL path for Swagger UI documentation
            redoc_url: URL path for ReDoc documentation
            openapi_url: URL path for OpenAPI JSON schema
            swagger_js_url: Custom Swagger UI JavaScript URL (optional)
            swagger_css_url: Custom Swagger UI CSS URL (optional)
            redoc_js_url: Custom ReDoc JavaScript URL (optional)
            use_cdn_fallback: Enable automatic fallback to local files if CDN fails
            prefer_local: Prefer local static files over CDN
            custom_css: Custom CSS to inject into documentation pages
            custom_js: Custom JavaScript to inject into documentation pages
            user_tags: Optional dictionary of username to allowed route tags.
                A user with tags only sees matching routes in the documentation.
                Users that are missing or mapped to None see everything.
            auth_method: "basic" for the browser's HTTP Basic prompt (default),
                or "form" for a login page with a session cookie and a logout link
            login_url: URL path of the login page (form login only)
            logout_url: URL path that ends the session (form login only)
            session_secret: Secret for signing the session cookie (form login
                only). Without it a random one is made at startup, which is
                fine for a single process. Set a long random value when the app
                runs in several worker processes or sessions should survive
                a restart.
            session_max_age: Lifetime of a session in seconds (form login only)
        """
        if auth_method not in AUTH_METHODS:
            raise ValueError(
                f"auth_method must be one of {AUTH_METHODS}, got {auth_method!r}"
            )

        # DocShield reads the Authorization header itself (see _basic_credentials).
        # The scheme stays here for code that uses it to protect its own routes.
        self.security = HTTPBasic()
        self.app = app
        self.credentials = credentials
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url
        self.swagger_js_url = swagger_js_url
        self.swagger_css_url = swagger_css_url
        self.redoc_js_url = redoc_js_url
        self.use_cdn_fallback = use_cdn_fallback
        self.prefer_local = prefer_local
        self.custom_css = custom_css
        self.custom_js = custom_js
        self.user_tags: Dict[str, Optional[Set[str]]] = {
            user: (set(tags) if tags is not None else None)
            for user, tags in (user_tags or {}).items()
        }
        self.auth_method = auth_method
        self.login_url = login_url
        self.logout_url = logout_url
        self.session_max_age = session_max_age
        if isinstance(session_secret, str):
            session_secret = session_secret.encode("utf-8")
        self._session_secret: bytes = session_secret or secrets.token_bytes(32)

        # Initialize static handler if fallback is enabled
        self.static_handler = (
            StaticHandler(app) if (use_cdn_fallback or prefer_local) else None
        )

        # Store original endpoints
        self.original_docs_url = app.docs_url
        self.original_redoc_url = app.redoc_url
        self.original_openapi_url = app.openapi_url
        self._oauth2_redirect_url: Optional[str] = getattr(
            app, "swagger_ui_oauth2_redirect_url", None
        )

        # Remove existing documentation routes
        self._remove_existing_docs_routes()

        # Disable built-in docs
        app.docs_url = None
        app.redoc_url = None
        app.openapi_url = None

        # Set up protected documentation routes
        self._setup_routes()

    def _remove_existing_docs_routes(self) -> None:
        """
        Remove FastAPI's own documentation routes from the app, so they
        don't answer without a login next to the protected ones.

        Only exact paths are removed. Other routes of the app stay,
        including ones that live under the docs path, like /docs/guide.
        """
        docs_paths = {
            self.original_docs_url,
            self.original_redoc_url,
            self.original_openapi_url,
            self._oauth2_redirect_url,
            self.docs_url,
            self.redoc_url,
            self.openapi_url,
        }
        self.app.router.routes[:] = [
            route
            for route in self.app.router.routes
            if getattr(route, "path", None) not in docs_paths
        ]

    # --- Authentication ---------------------------------------------------

    def _password_matches(self, username: str, password: str) -> bool:
        """Check a username and password against the credentials dictionary."""
        expected = self.credentials.get(username)
        # Compare even when the user doesn't exist, so the response time
        # doesn't show which usernames are valid. Bytes are compared because
        # compare_digest rejects text with non-ASCII characters.
        matches = secrets.compare_digest(
            password.encode("utf-8"), (expected or "").encode("utf-8")
        )
        return expected is not None and matches

    def _unauthorized(self) -> HTTPException:
        """The error for a request that isn't logged in."""
        headers = {"WWW-Authenticate": "Basic"} if self.auth_method == "basic" else None
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers=headers,
        )

    def _verify_credentials(self, credentials: HTTPBasicCredentials) -> str:
        """
        Verify HTTP Basic Auth credentials against our credentials dictionary.

        Args:
            credentials: The credentials provided by HTTPBasic

        Returns:
            The authenticated username if credentials are valid

        Raises:
            HTTPException: If authentication fails
        """
        if self._password_matches(credentials.username, credentials.password):
            return credentials.username
        raise self._unauthorized()

    @staticmethod
    def _basic_credentials(request: Request) -> Optional[Tuple[str, str]]:
        """
        Read the username and password of an HTTP Basic Authorization header.

        The header is decoded as UTF-8, which is what browsers send, so
        passwords with non-ASCII characters work.
        """
        scheme, _, param = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "basic":
            return None
        try:
            data = base64.b64decode(param.strip()).decode("utf-8")
        except ValueError:
            return None
        username, separator, password = data.partition(":")
        return (username, password) if separator else None

    def _authenticate(self, request: Request) -> Optional[str]:
        """
        Return the logged-in username, or None when the request has no valid login.

        HTTP Basic credentials are accepted with both auth methods, so scripts
        can fetch the schema when the pages use form login.
        """
        credentials = self._basic_credentials(request)
        if credentials is not None and self._password_matches(*credentials):
            return credentials[0]
        if self.auth_method == "form":
            return self._read_session(request.cookies.get(SESSION_COOKIE_NAME))
        return None

    # --- Session cookie (form login) ---------------------------------------

    def _sign(self, payload: str, username: str) -> str:
        """
        Sign a session payload with the session secret.

        The user's own password is part of the signed text, so the session
        stops working when that password changes. Without the secret a
        signature says nothing about any password.
        """
        message = f"{payload}.{self.credentials.get(username, '')}"
        return hmac.new(
            self._session_secret, message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def _create_session(self, username: str) -> str:
        """Create the signed cookie value for a logged-in user."""
        # The padding is dropped, so the cookie value needs no quoting
        user = base64.urlsafe_b64encode(username.encode("utf-8")).decode("ascii")
        payload = f"{user.rstrip('=')}.{int(time.time()) + self.session_max_age}"
        return f"{payload}.{self._sign(payload, username)}"

    def _read_session(self, token: Optional[str]) -> Optional[str]:
        """Return the username of a valid, unexpired session cookie, else None."""
        if not token:
            return None
        payload, _, signature = token.rpartition(".")
        user, _, expires = payload.partition(".")
        try:
            padded = user + "=" * (-len(user) % 4)
            username = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
            expired = int(expires) < time.time()
        except ValueError:
            return None
        if username not in self.credentials:
            return None
        if not hmac.compare_digest(
            signature.encode("utf-8"), self._sign(payload, username).encode("utf-8")
        ):
            return None
        return None if expired else username

    @staticmethod
    async def _read_login_form(request: Request) -> Dict[str, List[str]]:
        """
        Read the fields of the login form.

        The form has two short fields, so reading stops as soon as the body
        is larger than that. A body that is too large counts as an empty form.
        """
        try:
            declared_size = int(request.headers.get("content-length", "0"))
        except ValueError:
            return {}
        if declared_size > _MAX_LOGIN_BODY:
            return {}
        body = b""
        async for chunk in request.stream():
            body += chunk
            if len(body) > _MAX_LOGIN_BODY:
                return {}
        return parse_qs(body.decode("utf-8", "replace"))

    def _login_target(self, requested: Optional[str]) -> str:
        """Where to send the user after login. Only our own pages are allowed."""
        pages = []
        if self.original_docs_url is not None:
            pages.append(self.docs_url)
        if self.original_redoc_url is not None:
            pages.append(self.redoc_url)
        if requested in pages:
            return str(requested)
        return pages[0] if pages else self.openapi_url

    def _login_page(
        self, request: Request, next_url: str, failed: bool = False
    ) -> HTMLResponse:
        """Render the login page."""
        error = '<p class="error">Incorrect username or password</p>' if failed else ""
        content = _templates.render(
            _templates.LOGIN_PAGE,
            {
                "TITLE": html.escape(f"{self.app.title} - Log in"),
                "HEADING": html.escape(self.app.title),
                "ACTION": html.escape(_root_path(request) + self.login_url),
                "NEXT": html.escape(next_url),
                "ERROR": error,
            },
        )
        return HTMLResponse(
            content=content,
            status_code=status.HTTP_401_UNAUTHORIZED if failed else status.HTTP_200_OK,
            headers=NO_STORE,
        )

    def _login_required(self, request: Request, page_url: str) -> RedirectResponse:
        """Answer a page request that isn't logged in."""
        if self.auth_method == "basic":
            raise self._unauthorized()
        login_url = (
            f"{_root_path(request)}{self.login_url}?next={quote(page_url, safe='/')}"
        )
        return RedirectResponse(login_url, status_code=status.HTTP_303_SEE_OTHER)

    # --- OpenAPI schema -----------------------------------------------------

    @staticmethod
    def _collect_schema_refs(obj: Any, refs: Set[str]) -> None:
        """Recursively collect all referenced component schema names
        from an OpenAPI object."""
        if isinstance(obj, dict):
            ref = obj.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                refs.add(ref.split("/")[-1])
            for value in obj.values():
                DocShield._collect_schema_refs(value, refs)
        elif isinstance(obj, list):
            for item in obj:
                DocShield._collect_schema_refs(item, refs)

    @staticmethod
    def _filter_path_items(
        path_items: Dict[str, Any], allowed_tags: Set[str]
    ) -> Dict[str, Any]:
        """Keep the operations that carry an allowed tag. Untagged ones are dropped."""
        filtered: Dict[str, Any] = {}
        for path, path_item in path_items.items():
            if not isinstance(path_item, dict):
                continue
            allowed_operations = {}
            non_operation_fields = {}
            for key, value in path_item.items():
                if key.lower() in _HTTP_METHODS and isinstance(value, dict):
                    if set(value.get("tags", [])) & allowed_tags:
                        allowed_operations[key] = value
                else:
                    non_operation_fields[key] = value
            if allowed_operations:
                filtered[path] = {**non_operation_fields, **allowed_operations}
        return filtered

    def _filter_openapi_schema(
        self, schema: Dict[str, Any], username: str
    ) -> Dict[str, Any]:
        """
        Filter OpenAPI paths, webhooks, component schemas, and top-level tags
        for a user.

        Users omitted from user_tags or mapped to None receive the full schema.
        """
        allowed_tags = self.user_tags.get(username)
        if allowed_tags is None:
            return schema

        # Deep copy so we never mutate FastAPI's cached app.openapi() schema
        filtered_schema = copy.deepcopy(schema)

        # 1. Filter paths and webhooks by allowed tags
        visible: List[Any] = []
        for section in ("paths", "webhooks"):
            if isinstance(filtered_schema.get(section), dict):
                filtered_schema[section] = self._filter_path_items(
                    filtered_schema[section], allowed_tags
                )
                visible.append(filtered_schema[section])

        # 2. Prune components.schemas to only models referenced by what is
        # still visible (including nested refs)
        components = filtered_schema.get("components")
        if isinstance(components, dict) and isinstance(components.get("schemas"), dict):
            all_schemas = components["schemas"]
            pending: Set[str] = set()
            self._collect_schema_refs(visible, pending)

            used_schemas: Set[str] = set()
            while pending:
                schema_name = pending.pop()
                if schema_name in used_schemas or schema_name not in all_schemas:
                    continue
                used_schemas.add(schema_name)
                self._collect_schema_refs(all_schemas[schema_name], pending)

            components["schemas"] = {
                name: definition
                for name, definition in all_schemas.items()
                if name in used_schemas
            }

        # 3. Filter top-level tags metadata if present
        if isinstance(filtered_schema.get("tags"), list):
            filtered_schema["tags"] = [
                tag
                for tag in filtered_schema["tags"]
                if isinstance(tag, dict) and tag.get("name") in allowed_tags
            ]

        return filtered_schema

    def _openapi_schema(self, request: Request, username: str) -> Dict[str, Any]:
        """Build the OpenAPI schema for one request, the way FastAPI does."""
        schema = self.app.openapi()
        root_path = _root_path(request)
        if root_path and getattr(self.app, "root_path_in_servers", True):
            servers = schema.get("servers", [])
            if root_path not in {server.get("url") for server in servers}:
                schema = dict(schema)
                schema["servers"] = [{"url": root_path}] + servers
        return self._filter_openapi_schema(schema, username)

    # --- Documentation pages ------------------------------------------------

    def _local_url(self, request: Request, url: str) -> str:
        """Put the app's root path in front of a URL that this app serves."""
        if url.startswith(STATIC_URL_PREFIX):
            return _root_path(request) + url
        return url

    def _swagger_assets(self) -> Tuple[List[str], List[str]]:
        """The Swagger UI script and stylesheet URLs, in the order to try them."""
        if self.swagger_js_url is not None or self.swagger_css_url is not None:
            return (
                [self.swagger_js_url or SWAGGER_JS_CDN_URL],
                [self.swagger_css_url or SWAGGER_CSS_CDN_URL],
            )
        if self.static_handler and self.prefer_local:
            js_url, css_url = self.static_handler.get_swagger_urls(prefer_local=True)
            return [js_url], [css_url]
        if self.static_handler and self.use_cdn_fallback:
            return (
                [SWAGGER_JS_CDN_URL, SWAGGER_JS_LOCAL_URL],
                [SWAGGER_CSS_CDN_URL, SWAGGER_CSS_LOCAL_URL],
            )
        return [SWAGGER_JS_CDN_URL], [SWAGGER_CSS_CDN_URL]

    def _redoc_assets(self) -> List[str]:
        """The ReDoc script URLs, in the order to try them."""
        if self.redoc_js_url is not None:
            return [self.redoc_js_url]
        if self.static_handler and self.prefer_local:
            return [self.static_handler.get_redoc_url(prefer_local=True)]
        if self.static_handler and self.use_cdn_fallback:
            return [REDOC_JS_CDN_URL, REDOC_JS_LOCAL_URL]
        return [REDOC_JS_CDN_URL]

    def _page(
        self, request: Request, template: str, title: str, values: Dict[str, str]
    ) -> str:
        """Render a documentation page with the parts both pages share."""
        custom_style = (
            f'<style id="docshield-custom-css">{self.custom_css}</style>'
            if self.custom_css
            else ""
        )
        logout_link = ""
        if self.auth_method == "form":
            logout_url = html.escape(_root_path(request) + self.logout_url)
            logout_link = _templates.render(
                _templates.LOGOUT_LINK, {"LOGOUT_URL": logout_url}
            )
        shared = {
            "TITLE": html.escape(f"{self.app.title} - {title}"),
            "CUSTOM_STYLE": custom_style,
            "LOGOUT_LINK": logout_link,
            "LOADER": _templates.LOADER_SCRIPT,
            "CUSTOM_JS": self.custom_js or "// No custom JS",
        }
        return _templates.render(template, {**shared, **values})

    def _swagger_html(self, request: Request) -> str:
        """Render the Swagger UI page."""
        root_path = _root_path(request)
        js_urls, css_urls = self._swagger_assets()
        config = dict(_SWAGGER_UI_DEFAULTS)
        config.update(getattr(self.app, "swagger_ui_parameters", None) or {})
        config["url"] = root_path + self.openapi_url
        oauth2_redirect_url = (
            root_path + self._oauth2_redirect_url if self._oauth2_redirect_url else None
        )
        values = {
            "JS_URLS": _js([self._local_url(request, url) for url in js_urls]),
            "CSS_URLS": _js([self._local_url(request, url) for url in css_urls]),
            "CONFIG": _js(config),
            "OAUTH2_REDIRECT_URL": _js(oauth2_redirect_url),
            "INIT_OAUTH": _js(getattr(self.app, "swagger_ui_init_oauth", None)),
        }
        return self._page(request, _templates.SWAGGER_PAGE, "Swagger UI", values)

    def _redoc_html(self, request: Request) -> str:
        """Render the ReDoc page."""
        values = {
            "JS_URLS": _js(
                [self._local_url(request, url) for url in self._redoc_assets()]
            ),
            "OPENAPI_URL": html.escape(_root_path(request) + self.openapi_url),
        }
        return self._page(request, _templates.REDOC_PAGE, "ReDoc", values)

    # --- Routes ---------------------------------------------------------------

    def _setup_routes(self) -> None:
        """Set up all protected documentation endpoints."""
        app = self.app

        @app.get(self.openapi_url, include_in_schema=False)
        async def get_openapi(request: Request):
            username = self._authenticate(request)
            if username is None:
                raise self._unauthorized()
            return JSONResponse(
                self._openapi_schema(request, username), headers=NO_STORE
            )

        # Set up Swagger UI endpoint if the original app had it
        if self.original_docs_url is not None:

            @app.get(self.docs_url, include_in_schema=False)
            async def get_docs(request: Request):
                if self._authenticate(request) is None:
                    return self._login_required(request, self.docs_url)
                return HTMLResponse(self._swagger_html(request), headers=NO_STORE)

            if self._oauth2_redirect_url:

                @app.get(self._oauth2_redirect_url, include_in_schema=False)
                async def get_swagger_oauth2_redirect():
                    return get_swagger_ui_oauth2_redirect_html()

        # Set up ReDoc endpoint if the original app had it
        if self.original_redoc_url is not None:

            @app.get(self.redoc_url, include_in_schema=False)
            async def get_redoc(request: Request):
                if self._authenticate(request) is None:
                    return self._login_required(request, self.redoc_url)
                return HTMLResponse(self._redoc_html(request), headers=NO_STORE)

        if self.auth_method == "form":
            self._setup_login_routes()

    def _setup_login_routes(self) -> None:
        """Set up the login page and the logout URL for form login."""
        app = self.app

        @app.get(self.login_url, include_in_schema=False)
        async def get_login(request: Request):
            target = self._login_target(request.query_params.get("next"))
            if self._authenticate(request) is not None:
                return RedirectResponse(
                    _root_path(request) + target, status_code=status.HTTP_303_SEE_OTHER
                )
            return self._login_page(request, target)

        @app.post(self.login_url, include_in_schema=False)
        async def post_login(request: Request):
            form = await self._read_login_form(request)
            username = form.get("username", [""])[0]
            password = form.get("password", [""])[0]
            target = self._login_target(form.get("next", [None])[0])
            if not self._password_matches(username, password):
                return self._login_page(request, target, failed=True)

            response = RedirectResponse(
                _root_path(request) + target, status_code=status.HTTP_303_SEE_OTHER
            )
            response.set_cookie(
                SESSION_COOKIE_NAME,
                self._create_session(username),
                max_age=self.session_max_age,
                path=_root_path(request) or "/",
                secure=request.url.scheme == "https",
                httponly=True,
                samesite="lax",
            )
            return response

        @app.get(self.logout_url, include_in_schema=False)
        async def get_logout(request: Request):
            response = RedirectResponse(
                _root_path(request) + self.login_url,
                status_code=status.HTTP_303_SEE_OTHER,
            )
            response.delete_cookie(SESSION_COOKIE_NAME, path=_root_path(request) or "/")
            return response
