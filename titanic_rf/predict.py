"""Fungsi prediksi untuk satu penumpang baru."""

from __future__ import annotations

import pandas as pd

from .config import MODEL_PATH
from .model import load_bundle


def predict_survival(passenger_data: dict | pd.DataFrame, model_path=MODEL_PATH) -> dict:
    """Prediksi kelangsungan hidup beserta probabilitas untuk satu penumpang.

    passenger_data dapat berupa dict satu penumpang atau DataFrame satu baris.
    """
    bundle = load_bundle(model_path)
    model = bundle["model"]
    preprocessor = bundle["preprocessor"]

    if isinstance(passenger_data, dict):
        passenger_data = pd.DataFrame([passenger_data])
    elif isinstance(passenger_data, pd.Series):
        passenger_data = passenger_data.to_frame().T

    if len(passenger_data) != 1:
        raise ValueError("predict_survival hanya menerima satu baris data penumpang.")

    X = preprocessor.transform(passenger_data)
    prediction = int(model.predict(X)[0])
    probability = float(model.predict_proba(X)[0, 1])

    return {
        "prediksi": prediction,
        "label": "Selamat" if prediction == 1 else "Tidak Selamat",
        "probabilitas_selamat": round(probability, 4),
        "probabilitas_tidak_selamat": round(1 - probability, 4),
    }
