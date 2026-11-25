"""Entry point: jalankan seluruh alur kerja dengan `python main.py`."""

import argparse
from pathlib import Path

from sklearn.model_selection import train_test_split

from titanic_rf.config import (
    CONFUSION_MATRIX_PATH,
    FEATURE_IMPORTANCE_PATH,
    MODEL_PATH,
    RANDOM_STATE,
    TARGET,
    TEST_SIZE,
)
from titanic_rf.data import load_data, run_eda
from titanic_rf.features import TitanicPreprocessor
from titanic_rf.model import (
    evaluate_model,
    plot_confusion_matrix,
    plot_feature_importance,
    save_bundle,
    train_baseline,
    tune_model,
)
from titanic_rf.predict import predict_survival

SAMPLE_PASSENGER = {
    "Pclass": 1,
    "Name": "Smith, Mr. John",
    "Sex": "male",
    "Age": 30,
    "SibSp": 0,
    "Parch": 0,
    "Ticket": "PC 12345",
    "Fare": 50.0,
    "Cabin": "C85",
    "Embarked": "S",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Klasifikasi Titanic dengan Random Forest")
    parser.add_argument("--data", type=Path, default=None, help="Path ke Titanic-Dataset.csv.xls")
    parser.add_argument("--model-out", type=Path, default=MODEL_PATH, help="Path file model .pkl")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Tahap 1: muat data dan lakukan EDA singkat.
    df = load_data(args.data)
    run_eda(df)

    # Tahap 2: pisahkan data lebih awal agar imputasi hanya belajar dari data latih.
    X_raw = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    preprocessor = TitanicPreprocessor().fit(X_train_raw)
    X_train = preprocessor.transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    print("\n" + "=" * 60)
    print("TAHAP 2: PREPROCESSING & FEATURE ENGINEERING")
    print("=" * 60)
    print(f"Ukuran data latih : {X_train.shape}")
    print(f"Ukuran data uji   : {X_test.shape}")
    print(f"Fitur hasil encoding ({len(X_train.columns)}): {list(X_train.columns)}")

    # Tahap 3: baseline lalu tuning hyperparameter dengan 5-fold cross-validation.
    print("\n" + "=" * 60)
    print("TAHAP 3: PEMODELAN & HYPERPARAMETER TUNING")
    print("=" * 60)
    baseline = train_baseline(X_train, y_train)
    print("\n--- Evaluasi model baseline ---")
    evaluate_model(baseline, X_test, y_test)

    search = tune_model(X_train, y_train)
    best_model = search.best_estimator_
    print(f"\nParameter terbaik : {search.best_params_}")
    print(f"Skor ROC-AUC CV terbaik : {search.best_score_:.4f}")

    # Tahap 4: evaluasi akhir, confusion matrix, dan feature importance.
    print("\n" + "=" * 60)
    print("TAHAP 4: EVALUASI & INTERPRETASI MODEL")
    print("=" * 60)
    print("\n--- Evaluasi model terbaik pada data uji ---")
    evaluate_model(best_model, X_test, y_test)

    plot_confusion_matrix(best_model, X_test, y_test, CONFUSION_MATRIX_PATH)
    plot_feature_importance(best_model, list(X_train.columns), FEATURE_IMPORTANCE_PATH)

    # Tahap 5: simpan model dan uji satu prediksi penumpang baru.
    print("\n" + "=" * 60)
    print("TAHAP 5: PENYIMPANAN & SIMULASI PREDIKSI")
    print("=" * 60)
    bundle = {"model": best_model, "preprocessor": preprocessor}
    save_bundle(bundle, args.model_out)

    result = predict_survival(SAMPLE_PASSENGER, model_path=args.model_out)
    print(f"Contoh penumpang : {SAMPLE_PASSENGER}")
    print(f"Hasil prediksi   : {result}")


if __name__ == "__main__":
    main()
