"""Service prediksi: memuat bundle model dan menjalankan preprocessor training."""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import pandas as pd

from app.config import MODEL_PATH
from app.errors import ModelUnavailableError, PredictionError
from app.schemas import PassengerInput

LOGGER = logging.getLogger(__name__)


class TitanicModelService:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = Path(model_path)
        self.model = None
        self.preprocessor = None
        self.load_error: str | None = None

    def load(self) -> None:
        try:
            bundle = joblib.load(self.model_path)
            self.model = bundle["model"]
            self.preprocessor = bundle["preprocessor"]
            self.load_error = None
            LOGGER.info("Model Titanic berhasil dimuat dari %s", self.model_path)
        except Exception as exc:
            self.model = None
            self.preprocessor = None
            self.load_error = f"{type(exc).__name__}: {exc}"
            LOGGER.error("Gagal memuat model dari %s: %s", self.model_path, self.load_error)

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.preprocessor is not None

    def health(self) -> dict:
        if self.is_ready:
            return {
                "status": "ok",
                "model_loaded": True,
                "model_type": type(self.model).__name__,
                "feature_count": len(getattr(self.preprocessor, "feature_columns_", [])),
                "message": "Model dan preprocessor siap digunakan.",
            }
        return {
            "status": "degraded",
            "model_loaded": False,
            "model_type": None,
            "feature_count": None,
            "message": self.load_error or "Model belum dimuat.",
        }

    def predict(self, passenger: PassengerInput) -> dict:
        if not self.is_ready:
            raise ModelUnavailableError(
                "Model belum dimuat. Periksa file model dan jalankan ulang server."
            )

        try:
            raw = pd.DataFrame([passenger.to_raw_passenger()])
            features = self.preprocessor.transform(raw)
            probability = float(self.model.predict_proba(features)[0, 1])
            survived = int(self.model.predict(features)[0])

            if probability >= 0.75:
                risk_level = "Rendah"
            elif probability >= 0.40:
                risk_level = "Sedang"
            else:
                risk_level = "Tinggi"

            return {
                "survived": survived,
                "label": "Selamat" if survived == 1 else "Tidak Selamat",
                "probability_survived": round(probability, 4),
                "probability_not_survived": round(1 - probability, 4),
                "risk_level": risk_level,
            }
        except Exception as exc:
            LOGGER.exception("Prediksi gagal untuk data %s", passenger.model_dump())
            raise PredictionError(f"Gagal melakukan prediksi: {exc}") from exc
