"""
Static file handler for DocShield.

Serves the bundled Swagger UI and ReDoc files, so the documentation
still works when the CDN can't be reached.

Author: George Khananaev
License: MIT
Copyright (c) 2025 George Khananaev
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

from fastapi import FastAPI
from fastapi.responses import Response

STATIC_URL_PREFIX = "/docshield/static"

SWAGGER_JS_CDN_URL = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
)
SWAGGER_CSS_CDN_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
REDOC_JS_CDN_URL = "https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"

SWAGGER_JS_LOCAL_URL = f"{STATIC_URL_PREFIX}/swagger-ui-bundle.js"
SWAGGER_CSS_LOCAL_URL = f"{STATIC_URL_PREFIX}/swagger-ui.css"
REDOC_JS_LOCAL_URL = f"{STATIC_URL_PREFIX}/redoc.standalone.js"

# URL -> (path inside the static folder, media type)
_STATIC_FILES: Dict[str, Tuple[str, str]] = {
    SWAGGER_JS_LOCAL_URL: ("swagger/swagger-ui-bundle.js", "application/javascript"),
    SWAGGER_CSS_LOCAL_URL: ("swagger/swagger-ui.css", "text/css"),
    REDOC_JS_LOCAL_URL: ("redoc/redoc.standalone.js", "application/javascript"),
}


class StaticHandler:
    """Serves the bundled documentation files from the package."""

    def __init__(self, app: FastAPI):
        """Register the static file routes on the FastAPI app."""
        self.app = app
        self.static_dir = Path(__file__).parent / "static"
        self._cache: Dict[str, bytes] = {}
        self._setup_static_routes()

    def _setup_static_routes(self) -> None:
        """Set up one route per bundled file."""
        for url in _STATIC_FILES:
            self._add_static_route(url)

    def _add_static_route(self, url: str) -> None:
        relative_path, media_type = _STATIC_FILES[url]

        async def serve_static_file():
            content = self._read_file(relative_path)
            if content is None:
                return Response(
                    content="Not found", status_code=404, media_type="text/plain"
                )
            return Response(
                content=content,
                media_type=media_type,
                headers={"Cache-Control": "public, max-age=3600"},
            )

        self.app.get(url, include_in_schema=False)(serve_static_file)

    def _read_file(self, relative_path: str) -> Optional[bytes]:
        """Read a bundled file once and keep it in memory."""
        if relative_path not in self._cache:
            file_path = self.static_dir / relative_path
            if not file_path.is_file():
                return None
            self._cache[relative_path] = file_path.read_bytes()
        return self._cache[relative_path]

    def get_swagger_urls(self, prefer_local: bool = False) -> Tuple[str, str]:
        """
        Get the Swagger UI URLs.

        Args:
            prefer_local: If True, return the bundled files when they exist

        Returns:
            Tuple of (js_url, css_url)
        """
        if prefer_local and self._check_local_files("swagger"):
            return SWAGGER_JS_LOCAL_URL, SWAGGER_CSS_LOCAL_URL
        return SWAGGER_JS_CDN_URL, SWAGGER_CSS_CDN_URL

    def get_redoc_url(self, prefer_local: bool = False) -> str:
        """
        Get the ReDoc URL.

        Args:
            prefer_local: If True, return the bundled file when it exists

        Returns:
            ReDoc JavaScript URL
        """
        if prefer_local and self._check_local_files("redoc"):
            return REDOC_JS_LOCAL_URL
        return REDOC_JS_CDN_URL

    def _check_local_files(self, doc_type: str) -> bool:
        """
        Check if the bundled files exist.

        Args:
            doc_type: Either "swagger" or "redoc"

        Returns:
            True if all required files exist
        """
        if doc_type == "swagger":
            names = ["swagger/swagger-ui-bundle.js", "swagger/swagger-ui.css"]
        elif doc_type == "redoc":
            names = ["redoc/redoc.standalone.js"]
        else:
            return False
        return all((self.static_dir / name).is_file() for name in names)
