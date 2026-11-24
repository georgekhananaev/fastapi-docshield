"""
FastAPI DocShield - protect FastAPI's documentation endpoints with a login.

The package secures FastAPI's built-in documentation endpoints
(/docs, /redoc and /openapi.json) with HTTP Basic Authentication
or with a login page.

Author: George Khananaev
License: MIT License
Copyright (c) 2025 George Khananaev
"""

from ._version import __version__
from .docshield import DocShield

__author__ = "George Khananaev"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 George Khananaev"
__all__ = ["DocShield", "__version__"]
