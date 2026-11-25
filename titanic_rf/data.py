"""Pemuatan data dan eksplorasi data singkat (EDA)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DATA_FILENAME, ROOT_DIR, TARGET

EXPECTED_COLUMNS = {
    "PassengerId", "Pclass", "Name", "Sex", "Age", "SibSp",
    "Parch", "Ticket", "Fare", "Cabin", "Embarked", TARGET,
}


def resolve_data_path(explicit_path: Path | None = None) -> Path:
    """Cari file dataset di beberapa lokasi umum atau gunakan path eksplisit."""
    candidates: list[Path] = []
    if explicit_path is not None:
        candidates.append(Path(explicit_path).expanduser())

    base_dirs = [Path.cwd(), ROOT_DIR]
    for base in base_dirs:
        candidates.append(base / DATA_FILENAME)
        candidates.append(base / "data" / DATA_FILENAME)

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    searched = "\n  - ".join(str(c.resolve()) for c in candidates)
    raise FileNotFoundError(
        f"Dataset '{DATA_FILENAME}' tidak ditemukan. Letakkan file di salah satu lokasi:\n  - {searched}\n"
        "Atau jalankan: python main.py --data /path/ke/Titanic-Dataset.csv.xls"
    )


def load_data(path: Path | None = None) -> pd.DataFrame:
    """Baca dataset dengan read_csv meskipun ekstensinya .xls."""
    data_path = resolve_data_path(path)
    df = pd.read_csv(data_path)

    missing_columns = EXPECTED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Kolom yang diharapkan tidak ditemukan: {sorted(missing_columns)}")

    return df


def run_eda(df: pd.DataFrame) -> None:
    """Tampilkan ringkasan data, distribusi target, dan jumlah missing values."""
    print("\n" + "=" * 60)
    print("TAHAP 1: LOAD DATA & EDA SINGKAT")
    print("=" * 60)

    print(f"\nBentuk dataset : {df.shape[0]} baris x {df.shape[1]} kolom")
    print("\n--- 5 baris pertama ---")
    print(df.head().to_string())
    print("\n--- Tipe data ---")
    print(df.dtypes.to_string())
    print("\n--- Ringkasan statistik ---")
    print(df.describe(include="all").T.to_string())

    print("\n--- Distribusi kelas 'Survived' ---")
    counts = df[TARGET].value_counts().sort_index()
    percentages = df[TARGET].value_counts(normalize=True).sort_index() * 100
    class_summary = pd.DataFrame({
        "Jumlah": counts,
        "Persentase (%)": percentages.round(2),
    })
    class_summary.index = ["Tidak Selamat (0)", "Selamat (1)"]
    print(class_summary.to_string())

    print("\n--- Jumlah missing values ---")
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        print("Tidak ada missing values.")
    else:
        print(missing.to_string())
