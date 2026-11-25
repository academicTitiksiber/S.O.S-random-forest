"""Preprocessing dan feature engineering yang reusable untuk latih maupun prediksi."""

from __future__ import annotations

import re
import numpy as np
import pandas as pd

BASE_FEATURES = [
    "Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked",
    "HasCabin", "FamilySize", "IsAlone", "Title",
]
CATEGORICAL_FEATURES = ["Sex", "Embarked", "Title"]
TITLE_PATTERN = re.compile(r",\s*([^\.]+)\.")


def extract_title(name: object) -> str:
    """Ambil gelar dari format 'Last, Title. First' pada kolom Name."""
    if not isinstance(name, str):
        return "Unknown"
    match = TITLE_PATTERN.search(name)
    title = match.group(1).strip() if match else "Unknown"

    # Gelar langka dikelompokkan agar tidak terlalu banyak kategori.
    if title in {"Mlle", "Ms"}:
        return "Miss"
    if title == "Mme":
        return "Mrs"
    if title not in {"Mr", "Mrs", "Miss", "Master"}:
        return "Rare"
    return title


class TitanicPreprocessor:
    """Menyimpan statistik imputasi dan skema encoding dari data latih."""

    def fit(self, df: pd.DataFrame) -> "TitanicPreprocessor":
        """Pelajari median, modus, kategori, dan urutan kolom dari data latih."""
        work = df.copy()

        self.age_medians_ = work.groupby(["Pclass", "Sex"])["Age"].median()
        self.global_age_median_ = work["Age"].median()
        if pd.isna(self.global_age_median_):
            self.global_age_median_ = 0.0

        self.fare_median_ = work["Fare"].median()
        if pd.isna(self.fare_median_):
            self.fare_median_ = 0.0

        self.embarked_mode_ = self._mode_or_default(work.get("Embarked"), "S")
        self.sex_mode_ = self._mode_or_default(work.get("Sex"), "male")

        prepared = self._prepare_raw(work)
        self.categories_ = {
            col: sorted(prepared[col].dropna().astype(str).unique().tolist())
            for col in CATEGORICAL_FEATURES
        }
        self.feature_columns_ = self._encode(prepared).columns.tolist()
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ubah data mentah menjadi matriks fitur dengan urutan kolom identik."""
        prepared = self._prepare_raw(df)
        encoded = self._encode(prepared)
        return encoded.reindex(columns=self.feature_columns_, fill_value=0)

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Shortcut fit + transform untuk data latih."""
        return self.fit(df).transform(df)

    @staticmethod
    def _mode_or_default(series: pd.Series | None, default: str) -> str:
        if series is None or series.dropna().empty:
            return default
        return str(series.mode().iloc[0])

    def _prepare_raw(self, df: pd.DataFrame) -> pd.DataFrame:
        """Imputasi missing values dan buat fitur turunan."""
        out = pd.DataFrame(df).copy()

        # Pastikan kolom opsional ada saat dipakai untuk satu penumpang baru.
        for column in ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]:
            if column not in out.columns:
                out[column] = np.nan

        # Isi Age dengan median per (Pclass, Sex), lalu fallback ke median global.
        group_values = [
            self.age_medians_.get((pclass, sex), np.nan)
            for pclass, sex in zip(out["Pclass"], out["Sex"])
        ]
        out["Age"] = pd.to_numeric(out["Age"], errors="coerce")
        out["Age"] = out["Age"].fillna(pd.Series(group_values, index=out.index))
        out["Age"] = out["Age"].fillna(self.global_age_median_)

        out["Fare"] = pd.to_numeric(out["Fare"], errors="coerce").fillna(self.fare_median_)
        out["SibSp"] = pd.to_numeric(out["SibSp"], errors="coerce").fillna(0)
        out["Parch"] = pd.to_numeric(out["Parch"], errors="coerce").fillna(0)
        out["Pclass"] = pd.to_numeric(out["Pclass"], errors="coerce").fillna(3)

        # Cabin diubah menjadi indikator keberadaan kabin, lalu kolom aslinya dibuang.
        out["HasCabin"] = out["Cabin"].notna().astype(int) if "Cabin" in out.columns else 0

        # Feature engineering: ukuran keluarga, penumpang tunggal, dan gelar.
        out["FamilySize"] = out["SibSp"] + out["Parch"] + 1
        out["IsAlone"] = (out["FamilySize"] == 1).astype(int)
        out["Title"] = out["Name"].apply(extract_title) if "Name" in out.columns else "Unknown"

        out["Embarked"] = out["Embarked"].fillna(self.embarked_mode_) if "Embarked" in out.columns else self.embarked_mode_
        out["Sex"] = out["Sex"].fillna(self.sex_mode_)
        out["Embarked"] = out["Embarked"].astype(str)
        out["Sex"] = out["Sex"].astype(str)

        # Kolom PassengerId, Ticket, Name, dan Cabin sengaja tidak dipakai modeling.
        return out.reindex(columns=BASE_FEATURES)

    def _encode(self, prepared: pd.DataFrame) -> pd.DataFrame:
        """One-hot encoding dengan kategori tetap hasil fit, drop_first=True."""
        encoded = prepared.copy()
        for column in CATEGORICAL_FEATURES:
            encoded[column] = pd.Categorical(
                encoded[column].astype(str),
                categories=self.categories_[column],
            )

        dummies = pd.get_dummies(
            encoded[CATEGORICAL_FEATURES],
            prefix=CATEGORICAL_FEATURES,
            drop_first=True,
            dtype=int,
        )
        numeric = encoded.drop(columns=CATEGORICAL_FEATURES)
        return pd.concat([numeric, dummies], axis=1)
