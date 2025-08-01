"""
typed-api-response
------------------

A lightweight, fully type-safe API response builder for Python.

Usage:

>>> from typed_api_response import build_api_response, ResponseMeta
>>> build_api_response(data={"foo": "bar"}, status=200)
>>> build_api_response(error=ValueError("bad input"), status=400)

Only one of `data` or `error` must be provided.
Use `ResponseMeta` to attach version, timestamp, request ID, and other metadata.
All responses raise `ApiResponseBuilderError` on internal failure.

Framework-agnostic. Works with FastAPI, Django REST, Flask, or anything else.
"""

from .response import build_api_response
from .schemas import ResponseMeta
from .errors import ApiResponseBuilderError

__all__ = [
    "build_api_response",
    "ResponseMeta",
    "ApiResponseBuilderError",
]