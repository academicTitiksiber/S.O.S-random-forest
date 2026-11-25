"""Jenis error dan bentuk respons error yang konsisten."""

from __future__ import annotations


class ModelUnavailableError(RuntimeError):
    pass


class PredictionError(RuntimeError):
    pass


def error_body(code: str, message: str, details: list[dict] | None = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
        }
    }
