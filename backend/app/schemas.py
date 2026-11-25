"""Skema request dan response API prediksi keselamatan penumpang."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from titanic_rf.features import extract_title

ALLOWED_TITLES = ("Mr", "Mrs", "Miss", "Master", "Rare")
TITLE_OPTIONS = ", ".join(ALLOWED_TITLES)


class PassengerInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    pclass: int = Field(ge=1, le=3, description="Kelas penumpang: 1, 2, atau 3")
    sex: Literal["male", "female"]
    age: float = Field(ge=0.1, le=100)
    sibsp: int = Field(ge=0, le=20)
    parch: int = Field(ge=0, le=20)
    fare: float = Field(ge=0, le=1000)
    embarked: Literal["S", "C", "Q"]
    title: str | None = Field(default=None, max_length=30)
    name: str | None = Field(default=None, max_length=200)
    has_cabin: int = Field(default=0, ge=0, le=1)

    @field_validator("pclass", mode="before")
    @classmethod
    def coerce_pclass(cls, value):
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        return value

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        if not isinstance(value, str):
            raise ValueError("title harus berupa teks")
        for option in ALLOWED_TITLES:
            if value.strip().lower() == option.lower():
                return option
        raise ValueError(f"title harus salah satu dari: {TITLE_OPTIONS}")

    @field_validator("has_cabin", mode="before")
    @classmethod
    def normalize_has_cabin(cls, value):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "ya"}:
                return 1
            if normalized in {"0", "false", "no", "tidak"}:
                return 0
        return value

    @model_validator(mode="after")
    def resolve_title(self) -> "PassengerInput":
        if self.title is None:
            if not self.name:
                raise ValueError("Berikan salah satu dari 'title' atau 'name'")
            resolved = extract_title(self.name)
            if resolved not in ALLOWED_TITLES:
                raise ValueError(
                    f"Gelar hasil ekstraksi name ('{resolved}') tidak dikenali. "
                    f"Gunakan salah satu dari: {TITLE_OPTIONS}"
                )
            object.__setattr__(self, "title", resolved)
        return self

    def to_raw_passenger(self) -> dict:
        return {
            "Pclass": self.pclass,
            "Sex": self.sex,
            "Age": self.age,
            "SibSp": self.sibsp,
            "Parch": self.parch,
            "Fare": self.fare,
            "Embarked": self.embarked,
            "Name": f"Passenger, {self.title}. {self.sex}",
            "Cabin": "C85" if self.has_cabin else None,
        }


class PredictionResponse(BaseModel):
    survived: int
    label: str
    probability_survived: float
    probability_not_survived: float
    risk_level: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_type: str | None
    feature_count: int | None
    message: str
    api_version: str
