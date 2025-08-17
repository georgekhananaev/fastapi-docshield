"""
FastAPI DocShield - A simple module to protect FastAPI documentation endpoints with HTTP Basic Auth.

Author: George Khananaev
License: MIT
Copyright (c) 2025 George Khananaev
"""

__version__ = "0.2.1"

from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
import secrets
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
        
        # Initialize static handler if fallback is enabled
        self.static_handler = StaticHandler(app) if (use_cdn_fallback or prefer_local) else None
        
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
            if (path == self.original_docs_url or 
                path == self.original_redoc_url or 
                path == self.original_openapi_url or
                path == self.docs_url or 
                path == self.redoc_url or 
                path == self.openapi_url or
                path == "/docs" or  # Default docs
                path == "/redoc" or  # Default redoc
                path == "/openapi.json" or  # Default openapi
                path.startswith("/docs/") or  # Docs static files
                path.startswith(f"{self.docs_url}/")):  # New docs static files
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
    
    def _setup_routes(self) -> None:
        """
        Set up all protected documentation endpoints.
        
        Uses the stored swagger_js_url, swagger_css_url, and redoc_js_url.
        """
        # Set up OpenAPI JSON endpoint
        @self.app.get(self.openapi_url, include_in_schema=False)
        async def get_openapi(credentials: HTTPBasicCredentials = Depends(self.security)):
            self._verify_credentials(credentials)
            # Because we set app.openapi_url to None, we need to restore it temporarily
            old_openapi_url = self.app.openapi_url
            self.app.openapi_url = self.openapi_url
            openapi_schema = self.app.openapi()
            self.app.openapi_url = old_openapi_url
            return openapi_schema
        
        # Set up Swagger UI endpoint if the original app had it
        if self.original_docs_url is not None:
            @self.app.get(self.docs_url, include_in_schema=False)
            async def get_docs(credentials: HTTPBasicCredentials = Depends(self.security)):
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
                    js_url, css_url = self.static_handler.get_swagger_urls(prefer_local=True)
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
                    html_content = get_swagger_ui_html(**kwargs).body.decode('utf-8')
                    return HTMLResponse(self._inject_custom_code(html_content, is_swagger=True))
                
                return get_swagger_ui_html(**kwargs)
        
        # Set up ReDoc endpoint if the original app had it
        if self.original_redoc_url is not None:
            @self.app.get(self.redoc_url, include_in_schema=False)
            async def get_redoc(credentials: HTTPBasicCredentials = Depends(self.security)):
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
                    html_content = get_redoc_html(**kwargs).body.decode('utf-8')
                    return HTMLResponse(self._inject_custom_code(html_content, is_swagger=False))
                
                return get_redoc_html(**kwargs)
    
    def _get_swagger_with_fallback(self) -> HTMLResponse:
        """Generate Swagger UI HTML with automatic CDN fallback."""
        custom_styles = f"""
        <style>
            {self.custom_css if self.custom_css else ''}
        </style>
        """ if self.custom_css else ""
        
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
            {self.custom_js if self.custom_js else '// No custom JS'}
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
        custom_styles = f"""
        <style>
            {self.custom_css if self.custom_css else ''}
        </style>
        """ if self.custom_css else ""
        
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
            {self.custom_js if self.custom_js else '// No custom JS'}
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