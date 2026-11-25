from pathlib import Path

from fastapi.testclient import TestClient

from app.ml_service import TitanicModelService
from app.main import app

FIRST_CLASS = {
    "pclass": 1,
    "sex": "female",
    "age": 35,
    "sibsp": 1,
    "parch": 0,
    "fare": 80.0,
    "embarked": "C",
    "title": "Mrs",
    "has_cabin": 1,
}


def test_health_reports_loaded_model():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["model_loaded"] is True
        assert body["status"] == "ok"
        assert body["feature_count"] > 0


def test_predict_first_class_passenger():
    with TestClient(app) as client:
        response = client.post("/api/predict", json=FIRST_CLASS)
        assert response.status_code == 200
        body = response.json()
        assert set(body) == {
            "survived", "label", "probability_survived",
            "probability_not_survived", "risk_level",
        }
        assert body["survived"] in (0, 1)
        assert 0 <= body["probability_survived"] <= 1
        assert abs(body["probability_survived"] + body["probability_not_survived"] - 1) < 0.001
        assert body["risk_level"] in {"Rendah", "Sedang", "Tinggi"}


def test_predict_accepts_name_and_boolean_cabin():
    payload = {key: value for key, value in FIRST_CLASS.items() if key not in {"title", "has_cabin"}}
    payload["name"] = "Smith, Mrs. John"
    payload["has_cabin"] = True
    with TestClient(app) as client:
        direct = client.post("/api/predict", json=FIRST_CLASS)
        extracted = client.post("/api/predict", json=payload)
        assert extracted.status_code == 200
        assert extracted.json() == direct.json()


def test_validation_error_is_structured():
    with TestClient(app) as client:
        response = client.post("/api/predict", json={**FIRST_CLASS, "pclass": 4, "sex": "alien"})
        assert response.status_code == 422
        body = response.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"
        fields = {item["field"] for item in body["error"]["details"]}
        assert {"pclass", "sex"}.issubset(fields)


def test_unknown_title_via_name_maps_to_rare():
    payload = {key: value for key, value in FIRST_CLASS.items() if key != "title"}
    payload["name"] = "Smith, Mr John"
    with TestClient(app) as client:
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        assert response.json() == client.post(
            "/api/predict", json={**FIRST_CLASS, "title": "Rare"}
        ).json()


def test_invalid_explicit_title_is_rejected():
    with TestClient(app) as client:
        response = client.post("/api/predict", json={**FIRST_CLASS, "title": "Count"})
        assert response.status_code == 422
        details = response.json()["error"]["details"]
        assert any(item["field"] == "title" for item in details)


def test_model_not_loaded_returns_500():
    unavailable = TitanicModelService(Path("/does/not/exist.pkl"))
    with TestClient(app) as client:
        original = client.app.state.model_service
        try:
            client.app.state.model_service = unavailable
            health = client.get("/api/health")
            assert health.status_code == 200
            assert health.json()["model_loaded"] is False
            prediction = client.post("/api/predict", json=FIRST_CLASS)
            assert prediction.status_code == 500
            assert prediction.json()["error"]["code"] == "MODEL_NOT_LOADED"
        finally:
            client.app.state.model_service = original
