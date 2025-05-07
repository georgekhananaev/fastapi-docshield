"""
FastAPI DocShield - A simple package to protect FastAPI documentation endpoints with authentication.

This package provides an easy way to secure FastAPI's built-in documentation endpoints
(/docs, /redoc, /openapi.json) with HTTP Basic Authentication.

Author: George Khananaev
License: MIT License
Copyright (c) 2025 George Khananaev
"""

from .docshield import DocShield

__version__ = "0.1.0"
__author__ = "George Khananaev"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 George Khananaev"
__all__ = ["DocShield"]