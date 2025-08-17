"""
Static file handler for DocShield with CDN fallback support.

This module provides functionality to serve documentation static files
either from CDN or local storage as a fallback.

Author: George Khananaev
License: MIT
Copyright (c) 2025 George Khananaev
"""

import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import logging

logger = logging.getLogger(__name__)

class StaticHandler:
    """Handles static file serving with CDN fallback support."""
    
    def __init__(self, app: FastAPI):
        """Initialize the static handler with the FastAPI app."""
        self.app = app
        self.static_dir = Path(__file__).parent / "static"
        self._setup_static_routes()
    
    def _setup_static_routes(self):
        """Set up routes for serving local static files."""
        
        @self.app.get("/docshield/static/swagger-ui-bundle.js", include_in_schema=False)
        async def serve_swagger_js():
            """Serve Swagger UI JavaScript bundle."""
            file_path = self.static_dir / "swagger" / "swagger-ui-bundle.js"
            if file_path.exists():
                return FileResponse(
                    file_path,
                    media_type="application/javascript",
                    headers={"Cache-Control": "public, max-age=3600"}
                )
            return Response(content="// Swagger UI bundle not found", status_code=404)
        
        @self.app.get("/docshield/static/swagger-ui.css", include_in_schema=False)
        async def serve_swagger_css():
            """Serve Swagger UI CSS."""
            file_path = self.static_dir / "swagger" / "swagger-ui.css"
            if file_path.exists():
                return FileResponse(
                    file_path,
                    media_type="text/css",
                    headers={"Cache-Control": "public, max-age=3600"}
                )
            return Response(content="/* Swagger UI CSS not found */", status_code=404)
        
        @self.app.get("/docshield/static/redoc.standalone.js", include_in_schema=False)
        async def serve_redoc_js():
            """Serve ReDoc JavaScript bundle."""
            file_path = self.static_dir / "redoc" / "redoc.standalone.js"
            if file_path.exists():
                return FileResponse(
                    file_path,
                    media_type="application/javascript",
                    headers={"Cache-Control": "public, max-age=3600"}
                )
            return Response(content="// ReDoc bundle not found", status_code=404)
    
    def get_swagger_urls(self, prefer_local: bool = False) -> tuple[str, str]:
        """
        Get Swagger UI URLs based on preference and availability.
        
        Args:
            prefer_local: If True, prefer local files over CDN
            
        Returns:
            Tuple of (js_url, css_url)
        """
        if prefer_local and self._check_local_files("swagger"):
            return (
                "/docshield/static/swagger-ui-bundle.js",
                "/docshield/static/swagger-ui.css"
            )
        
        # Default to CDN
        return (
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
        )
    
    def get_redoc_url(self, prefer_local: bool = False) -> str:
        """
        Get ReDoc URL based on preference and availability.
        
        Args:
            prefer_local: If True, prefer local files over CDN
            
        Returns:
            ReDoc JavaScript URL
        """
        if prefer_local and self._check_local_files("redoc"):
            return "/docshield/static/redoc.standalone.js"
        
        # Default to CDN
        return "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    
    def _check_local_files(self, doc_type: str) -> bool:
        """
        Check if local static files exist.
        
        Args:
            doc_type: Either "swagger" or "redoc"
            
        Returns:
            True if all required files exist
        """
        if doc_type == "swagger":
            js_file = self.static_dir / "swagger" / "swagger-ui-bundle.js"
            css_file = self.static_dir / "swagger" / "swagger-ui.css"
            return js_file.exists() and css_file.exists()
        elif doc_type == "redoc":
            js_file = self.static_dir / "redoc" / "redoc.standalone.js"
            return js_file.exists()
        return False
    
    def get_fallback_html(self, doc_type: str) -> str:
        """
        Generate HTML with automatic CDN fallback to local files.
        
        Args:
            doc_type: Either "swagger" or "redoc"
            
        Returns:
            HTML string with fallback logic
        """
        if doc_type == "swagger":
            return self._get_swagger_fallback_html()
        elif doc_type == "redoc":
            return self._get_redoc_fallback_html()
        return ""
    
    def _get_swagger_fallback_html(self) -> str:
        """Generate Swagger UI HTML with CDN fallback."""
        return """
        <script>
        // Try to load from CDN first, fallback to local if failed
        function loadSwaggerUI() {
            var script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js';
            script.onerror = function() {
                // CDN failed, try local
                console.warn('CDN failed, loading local Swagger UI');
                var localScript = document.createElement('script');
                localScript.src = '/docshield/static/swagger-ui-bundle.js';
                document.head.appendChild(localScript);
            };
            document.head.appendChild(script);
        }
        
        function loadSwaggerCSS() {
            var link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css';
            link.onerror = function() {
                // CDN failed, try local
                console.warn('CDN failed, loading local Swagger CSS');
                var localLink = document.createElement('link');
                localLink.rel = 'stylesheet';
                localLink.href = '/docshield/static/swagger-ui.css';
                document.head.appendChild(localLink);
            };
            document.head.appendChild(link);
        }
        
        loadSwaggerCSS();
        loadSwaggerUI();
        </script>
        """
    
    def _get_redoc_fallback_html(self) -> str:
        """Generate ReDoc HTML with CDN fallback."""
        return """
        <script>
        // Try to load from CDN first, fallback to local if failed
        function loadReDoc() {
            var script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js';
            script.onerror = function() {
                // CDN failed, try local
                console.warn('CDN failed, loading local ReDoc');
                var localScript = document.createElement('script');
                localScript.src = '/docshield/static/redoc.standalone.js';
                document.head.appendChild(localScript);
            };
            document.head.appendChild(script);
        }
        
        loadReDoc();
        </script>
        """