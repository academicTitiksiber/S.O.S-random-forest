"""Pelatihan, tuning, evaluasi, visualisasi, dan penyimpanan model Random Forest."""

from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")  # Aman dijalankan tanpa tampilan GUI.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

from .config import CV_FOLDS, N_ITER_SEARCH, RANDOM_STATE

PARAM_DISTRIBUTIONS = {
    "n_estimators": [100, 200, 300, 400],
    "max_depth": [None, 5, 8, 12, 16],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}


def train_baseline(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Latih model baseline Random Forest dengan parameter default."""
    model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
    model.fit(X_train, y_train)
    return model


def tune_model(X_train: pd.DataFrame, y_train: pd.Series) -> RandomizedSearchCV:
    """Cari kombinasi hyperparameter terbaik dengan 5-fold stratified CV."""
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    search = RandomizedSearchCV(
        estimator=RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        param_distributions=PARAM_DISTRIBUTIONS,
        n_iter=N_ITER_SEARCH,
        scoring="roc_auc",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        return_train_score=False,
    )
    search.fit(X_train, y_train)
    return search


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    """Hitung dan tampilkan metrik klasifikasi pada data uji."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1-Score": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, y_prob),
    }

    for name, value in metrics.items():
        print(f"{name:<12}: {value:.4f}")

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=["Tidak Selamat", "Selamat"], zero_division=0))
    return metrics


def plot_confusion_matrix(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    output_path,
) -> np.ndarray:
    """Tampilkan confusion matrix sebagai teks dan simpan visualisasi heatmap."""
    cm = confusion_matrix(y_test, model.predict(X_test))
    print("\n--- Confusion Matrix (baris=aktual, kolom=prediksi) ---")
    print(pd.DataFrame(
        cm,
        index=["Aktual: Tidak Selamat", "Aktual: Selamat"],
        columns=["Prediksi: Tidak Selamat", "Prediksi: Selamat"],
    ).to_string())

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Tidak Selamat", "Selamat"],
        yticklabels=["Tidak Selamat", "Selamat"],
        ax=ax,
    )
    ax.set_xlabel("Kelas Prediksi")
    ax.set_ylabel("Kelas Aktual")
    ax.set_title("Confusion Matrix - Random Forest (Titanic)")
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Visualisasi disimpan di: {output_path}")
    return cm


def plot_feature_importance(
    model: RandomForestClassifier,
    feature_names: list[str],
    output_path,
    top_n: int = 15,
) -> pd.Series:
    """Tampilkan dan simpan ranking feature importance."""
    importance = pd.Series(model.feature_importances_, index=feature_names)
    importance = importance.sort_values(ascending=False)

    print("\n--- Feature Importance (teratas) ---")
    print(importance.head(top_n).round(4).to_string())

    top = importance.head(top_n).sort_values()
    fig, ax = plt.subplots(figsize=(8, 6))
    top.plot(kind="barh", ax=ax, color="#4C72B0")
    ax.set_xlabel("Importance (penurunan impurity)")
    ax.set_title("Feature Importance - Random Forest (Titanic)")
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Visualisasi disimpan di: {output_path}")
    return importance


def save_bundle(bundle: dict, path) -> None:
    """Simpan model beserta preprocessor agar prediksi baru konsisten."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)
    print(f"\nModel tersimpan di: {path}")


def load_bundle(path):
    """Muat model dan preprocessor hasil pelatihan."""
    return joblib.load(Path(path))
