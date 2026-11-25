"""Konfigurasi lingkungan backend Titanic Safety API."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")


def _resolve_path(value: str | Path, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _parse_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


MODEL_PATH = _resolve_path(
    os.getenv("MODEL_PATH", BACKEND_DIR / "models" / "titanic_rf_model.pkl"),
    BACKEND_DIR,
)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
ALLOWED_ORIGINS = _parse_origins(
    os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5055,http://127.0.0.1:5055,http://localhost:5000,http://localhost:3000",
    )
)
API_TITLE = "Titanic Passenger Safety Prediction API"
API_VERSION = "1.0.0"
