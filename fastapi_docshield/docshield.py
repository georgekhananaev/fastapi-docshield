"""
FastAPI DocShield - A simple module to protect FastAPI documentation endpoints with HTTP Basic Auth.

Author: George Khananaev
License: MIT
Copyright (c) 2025 George Khananaev
"""

__version__ = "0.2.1"

import copy
import secrets
from collections.abc import Iterable
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .static_handler import StaticHandler


class DocShield:
    """
    DocShield provides authentication protection for FastAPI's built-in documentation endpoints.

    This class allows you to easily secure both /docs (Swagger UI) and /redoc endpoints
    with HTTP Basic Authentication.

    Author: George Khananaev
    License: MIT License
    """

    def __init__(
        self,
        app: FastAPI,
        credentials: dict[str, str],
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        openapi_url: str = "/openapi.json",
        swagger_js_url: str | None = None,
        swagger_css_url: str | None = None,
        redoc_js_url: str | None = None,
        use_cdn_fallback: bool = True,
        prefer_local: bool = False,
        custom_css: str | None = None,
        custom_js: str | None = None,
        user_tags: dict[str, Iterable[str] | None] | None = None,
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
            user_tags: Optional dictionary of user-defined tags for documentation
        """
        # Initialize security scheme
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
        self.user_tags: dict[str, set[str] | None] = {
            user: (set(tags) if tags is not None else None)
            for user, tags in (user_tags or {}).items()
        }

        # Initialize static handler if fallback is enabled
        self.static_handler = (
            StaticHandler(app) if (use_cdn_fallback or prefer_local) else None
        )

        # Store original endpoints
        self.original_docs_url = app.docs_url
        self.original_redoc_url = app.redoc_url
        self.original_openapi_url = app.openapi_url

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
        Remove the existing documentation routes from the FastAPI app.
        This ensures the default routes don't conflict with our secured ones.
        """
        # Since FastAPI.routes is a property with no setter, we have to use the underlying router
        # Get all non-documentation routes
        routes_to_keep = []

        # Identify and filter out documentation routes
        for route in self.app.routes:
            path = getattr(route, "path", "")

            # Skip both original and new documentation routes
            if (
                path == self.original_docs_url
                or path == self.original_redoc_url
                or path == self.original_openapi_url
                or path == self.docs_url
                or path == self.redoc_url
                or path == self.openapi_url
                or path == "/docs"  # Default docs
                or path == "/redoc"  # Default redoc
                or path == "/openapi.json"  # Default openapi
                or path.startswith("/docs/")  # Docs static files
                or path.startswith(f"{self.docs_url}/")
            ):  # New docs static files
                continue

            routes_to_keep.append(route)

        # Use a different approach - set up a fresh router and add all non-docs routes
        # We can access the router directly
        self.app.router.routes = routes_to_keep

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
        username = credentials.username
        password = credentials.password

        # Check if username exists and password is correct
        if username in self.credentials:
            is_correct_password = secrets.compare_digest(
                password,
                self.credentials[username],
            )
            if is_correct_password:
                return username

        # If credentials are invalid, raise an exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    @staticmethod
    def _collect_schema_refs(obj: Any, refs: set[str]) -> None:
        """Recursively collect all referenced component schema names from an OpenAPI object."""
        if isinstance(obj, dict):
            ref = obj.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                refs.add(ref.split("/")[-1])
            for value in obj.values():
                DocShield._collect_schema_refs(value, refs)
        elif isinstance(obj, list):
            for item in obj:
                DocShield._collect_schema_refs(item, refs)

    def _filter_openapi_schema(
        self, schema: dict[str, Any], username: str
    ) -> dict[str, Any]:
        """
        Filter OpenAPI paths, component schemas, and top-level tags for a user.
        Users omitted from user_tags or mapped to None receive the full schema.
        """
        allowed_tags = self.user_tags.get(username)
        if allowed_tags is None:
            return schema

        # Deep copy so we never mutate FastAPI's cached app.openapi() schema
        filtered_schema = copy.deepcopy(schema)
        http_methods = {
            "get",
            "put",
            "post",
            "delete",
            "options",
            "head",
            "patch",
            "trace",
        }

        # 1. Filter paths by allowed tags (untagged routes are excluded)
        filtered_paths: dict[str, Any] = {}
        for path, path_item in filtered_schema.get("paths", {}).items():
            if not isinstance(path_item, dict):
                continue

            allowed_operations = {}
            non_operation_fields = {}

            for key, value in path_item.items():
                if key.lower() in http_methods and isinstance(value, dict):
                    route_tags = set(value.get("tags", []))
                    if route_tags & allowed_tags:
                        allowed_operations[key] = value
                else:
                    non_operation_fields[key] = value

            if allowed_operations:
                filtered_paths[path] = {**non_operation_fields, **allowed_operations}

        filtered_schema["paths"] = filtered_paths

        # 2. Prune components.schemas to only models referenced by visible paths (including nested refs)
        components = filtered_schema.get("components")
        if isinstance(components, dict) and isinstance(components.get("schemas"), dict):
            all_schemas = components["schemas"]
            pending: set[str] = set()
            self._collect_schema_refs(filtered_paths, pending)

            used_schemas: set[str] = set()
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
        if "tags" in filtered_schema and isinstance(filtered_schema["tags"], list):
            filtered_schema["tags"] = [
                tag
                for tag in filtered_schema["tags"]
                if isinstance(tag, dict) and tag.get("name") in allowed_tags
            ]

        return filtered_schema

    def _setup_routes(self) -> None:
        """
        Set up all protected documentation endpoints.

        Uses the stored swagger_js_url, swagger_css_url, and redoc_js_url.
        """

        # Set up OpenAPI JSON endpoint
        @self.app.get(self.openapi_url, include_in_schema=False)
        async def get_openapi(
            credentials: HTTPBasicCredentials = Depends(self.security),
        ):
            username = self._verify_credentials(credentials)
            # Because we set app.openapi_url to None, we need to restore it temporarily
            old_openapi_url = self.app.openapi_url
            self.app.openapi_url = self.openapi_url
            openapi_schema = self.app.openapi()
            self.app.openapi_url = old_openapi_url
            return self._filter_openapi_schema(openapi_schema, username)

        # Set up Swagger UI endpoint if the original app had it
        if self.original_docs_url is not None:

            @self.app.get(self.docs_url, include_in_schema=False)
            async def get_docs(
                credentials: HTTPBasicCredentials = Depends(self.security),
            ):
                self._verify_credentials(credentials)

                # Determine which URLs to use
                if self.swagger_js_url is not None or self.swagger_css_url is not None:
                    # User provided custom URLs, use them
                    kwargs = {
                        "openapi_url": self.openapi_url,
                        "title": self.app.title + " - Swagger UI",
                    }
                    if self.swagger_js_url is not None:
                        kwargs["swagger_js_url"] = self.swagger_js_url
                    if self.swagger_css_url is not None:
                        kwargs["swagger_css_url"] = self.swagger_css_url
                elif self.static_handler and self.prefer_local:
                    # Prefer local files
                    js_url, css_url = self.static_handler.get_swagger_urls(
                        prefer_local=True
                    )
                    kwargs = {
                        "openapi_url": self.openapi_url,
                        "title": self.app.title + " - Swagger UI",
                        "swagger_js_url": js_url,
                        "swagger_css_url": css_url,
                    }
                elif self.static_handler and self.use_cdn_fallback:
                    # Use CDN with fallback support
                    return self._get_swagger_with_fallback()
                else:
                    # Default behavior - use CDN
                    kwargs = {
                        "openapi_url": self.openapi_url,
                        "title": self.app.title + " - Swagger UI",
                    }

                # If custom CSS/JS provided and not using fallback mode, wrap the response
                if self.custom_css or self.custom_js:
                    html_content = get_swagger_ui_html(**kwargs).body.decode("utf-8")
                    return HTMLResponse(
                        self._inject_custom_code(html_content, is_swagger=True)
                    )

                return get_swagger_ui_html(**kwargs)

        # Set up ReDoc endpoint if the original app had it
        if self.original_redoc_url is not None:

            @self.app.get(self.redoc_url, include_in_schema=False)
            async def get_redoc(
                credentials: HTTPBasicCredentials = Depends(self.security),
            ):
                self._verify_credentials(credentials)

                # Determine which URL to use
                if self.redoc_js_url is not None:
                    # User provided custom URL, use it
                    kwargs = {
                        "openapi_url": self.openapi_url,
                        "title": self.app.title + " - ReDoc",
                        "redoc_js_url": self.redoc_js_url,
                    }
                elif self.static_handler and self.prefer_local:
                    # Prefer local files
                    js_url = self.static_handler.get_redoc_url(prefer_local=True)
                    kwargs = {
                        "openapi_url": self.openapi_url,
                        "title": self.app.title + " - ReDoc",
                        "redoc_js_url": js_url,
                    }
                elif self.static_handler and self.use_cdn_fallback:
                    # Use CDN with fallback support
                    return self._get_redoc_with_fallback()
                else:
                    # Default behavior - use CDN
                    kwargs = {
                        "openapi_url": self.openapi_url,
                        "title": self.app.title + " - ReDoc",
                    }

                # If custom CSS/JS provided and not using fallback mode, wrap the response
                if self.custom_css or self.custom_js:
                    html_content = get_redoc_html(**kwargs).body.decode("utf-8")
                    return HTMLResponse(
                        self._inject_custom_code(html_content, is_swagger=False)
                    )

                return get_redoc_html(**kwargs)

    def _get_swagger_with_fallback(self) -> HTMLResponse:
        """Generate Swagger UI HTML with automatic CDN fallback."""
        custom_styles = (
            f"""
        <style>
            {self.custom_css if self.custom_css else ""}
        </style>
        """
            if self.custom_css
            else ""
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>{self.app.title} - Swagger UI</title>
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <style>
            body {{ margin: 0; }}
            #swagger-ui {{ display: flex; flex-direction: column; height: 100vh; }}
        </style>
        {custom_styles}
        </head>
        <body>
        <div id="swagger-ui"></div>

        <script>
        var cdnFailed = false;

        function loadSwaggerCSS() {{
            return new Promise((resolve, reject) => {{
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css';
                link.onload = resolve;
                link.onerror = () => {{
                    console.warn('CDN CSS failed, loading local Swagger CSS');
                    var localLink = document.createElement('link');
                    localLink.rel = 'stylesheet';
                    localLink.href = '/docshield/static/swagger-ui.css';
                    localLink.onload = resolve;
                    localLink.onerror = reject;
                    document.head.appendChild(localLink);
                }};
                document.head.appendChild(link);
            }});
        }}

        function loadSwaggerJS() {{
            return new Promise((resolve, reject) => {{
                var script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js';
                script.onload = resolve;
                script.onerror = () => {{
                    console.warn('CDN JS failed, loading local Swagger JS');
                    cdnFailed = true;
                    var localScript = document.createElement('script');
                    localScript.src = '/docshield/static/swagger-ui-bundle.js';
                    localScript.onload = resolve;
                    localScript.onerror = reject;
                    document.head.appendChild(localScript);
                }};
                document.head.appendChild(script);
            }});
        }}

        Promise.all([loadSwaggerCSS(), loadSwaggerJS()]).then(() => {{
            const ui = SwaggerUIBundle({{
                url: '{self.openapi_url}',
                dom_id: '#swagger-ui',
                layout: 'BaseLayout',
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
            }});
            if (cdnFailed) {{
                console.log('Documentation loaded using local fallback');
            }}

            // Custom JavaScript
            {self.custom_js if self.custom_js else "// No custom JS"}
        }}).catch(error => {{
            console.error('Failed to load Swagger UI:', error);
            document.getElementById('swagger-ui').innerHTML = '<h2>Failed to load documentation</h2>';
        }});
        </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    def _get_redoc_with_fallback(self) -> HTMLResponse:
        """Generate ReDoc HTML with automatic CDN fallback."""
        custom_styles = (
            f"""
        <style>
            {self.custom_css if self.custom_css else ""}
        </style>
        """
            if self.custom_css
            else ""
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>{self.app.title} - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 0; }}
        </style>
        {custom_styles}
        </head>
        <body>
        <redoc spec-url="{self.openapi_url}"></redoc>

        <script>
        function loadReDoc() {{
            return new Promise((resolve, reject) => {{
                var script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js';
                script.onload = resolve;
                script.onerror = () => {{
                    console.warn('CDN failed, loading local ReDoc');
                    var localScript = document.createElement('script');
                    localScript.src = '/docshield/static/redoc.standalone.js';
                    localScript.onload = resolve;
                    localScript.onerror = reject;
                    document.head.appendChild(localScript);
                }};
                document.head.appendChild(script);
            }});
        }}

        loadReDoc().then(() => {{
            console.log('ReDoc loaded successfully');

            // Custom JavaScript
            {self.custom_js if self.custom_js else "// No custom JS"}
        }}).catch(error => {{
            console.error('Failed to load ReDoc:', error);
            document.body.innerHTML = '<h2>Failed to load documentation</h2>';
        }});
        </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    def _inject_custom_code(self, html: str, is_swagger: bool = True) -> str:
        """Inject custom CSS and JavaScript into the HTML."""
        if self.custom_css:
            # Inject custom CSS before closing head tag
            css_injection = f"<style>{self.custom_css}</style></head>"
            html = html.replace("</head>", css_injection)

        if self.custom_js:
            # Inject custom JS before closing body tag
            js_injection = f"<script>{self.custom_js}</script></body>"
            html = html.replace("</body>", js_injection)

        return html
