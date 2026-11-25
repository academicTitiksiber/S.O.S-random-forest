"""Konfigurasi pusat untuk seluruh tahapan proyek Titanic Random Forest."""

from pathlib import Path

# Nama file dataset (ekstensi .xls, tetapi isinya CSV).
DATA_FILENAME = "Titanic-Dataset.csv.xls"

# Kolom target dan kolom yang tidak dipakai sebagai fitur mentah.
TARGET = "Survived"

# Pengaturan eksperimen.
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
N_ITER_SEARCH = 20

# Lokasi keluaran.
ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "titanic_rf_model.pkl"
OUTPUT_DIR = ROOT_DIR / "outputs"
CONFUSION_MATRIX_PATH = OUTPUT_DIR / "confusion_matrix.png"
FEATURE_IMPORTANCE_PATH = OUTPUT_DIR / "feature_importance.png"
