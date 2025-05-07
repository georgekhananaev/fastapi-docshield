"""
FastAPI DocShield - A simple module to protect FastAPI documentation endpoints with HTTP Basic Auth.

Author: George Khananaev
License: MIT
Copyright (c) 2025 George Khananaev
"""

from typing import Dict, Optional, Tuple
from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import base64


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
        """
        # Initialize security scheme
        self.security = HTTPBasic()
        self.app = app
        self.credentials = credentials
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url
        
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
        self._setup_routes(
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
            redoc_js_url=redoc_js_url
        )
    
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
            
            # Skip documentation routes
            if (path == self.docs_url or 
                path == self.redoc_url or 
                path == self.openapi_url or
                path.startswith(f"{self.docs_url}/") or  # Docs static files
                path == "/openapi.json"):
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
    
    def _setup_routes(
        self,
        swagger_js_url: Optional[str],
        swagger_css_url: Optional[str],
        redoc_js_url: Optional[str],
    ) -> None:
        """
        Set up all protected documentation endpoints.
        
        Args:
            swagger_js_url: Custom Swagger UI JavaScript URL
            swagger_css_url: Custom Swagger UI CSS URL
            redoc_js_url: Custom ReDoc JavaScript URL
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
                return get_swagger_ui_html(
                    openapi_url=self.openapi_url,
                    title=self.app.title + " - Swagger UI",
                    oauth2_redirect_url=None,
                    swagger_js_url=swagger_js_url,
                    swagger_css_url=swagger_css_url,
                )
        
        # Set up ReDoc endpoint if the original app had it
        if self.original_redoc_url is not None:
            @self.app.get(self.redoc_url, include_in_schema=False)
            async def get_redoc(credentials: HTTPBasicCredentials = Depends(self.security)):
                self._verify_credentials(credentials)
                return get_redoc_html(
                    openapi_url=self.openapi_url,
                    title=self.app.title + " - ReDoc",
                    redoc_js_url=redoc_js_url,
                )