"""Modul alur kerja klasifikasi keselamatan penumpang Titanic."""

from .data import load_data, run_eda
from .features import TitanicPreprocessor, extract_title
from .model import (
    evaluate_model,
    load_bundle,
    plot_confusion_matrix,
    plot_feature_importance,
    save_bundle,
    train_baseline,
    tune_model,
)
from .predict import predict_survival

__all__ = [
    "load_data", "run_eda", "TitanicPreprocessor", "extract_title",
    "evaluate_model", "load_bundle", "plot_confusion_matrix",
    "plot_feature_importance", "save_bundle", "train_baseline", "tune_model",
    "predict_survival",
]
