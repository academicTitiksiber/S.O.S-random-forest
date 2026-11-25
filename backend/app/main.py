"""FastAPI application: health check, prediksi, CORS, dan error handler."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import API_TITLE, API_VERSION, ALLOWED_ORIGINS
from app.errors import ModelUnavailableError, PredictionError, error_body
from app.ml_service import TitanicModelService
from app.schemas import HealthResponse, PassengerInput, PredictionResponse

model_service = TitanicModelService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_service.load()
    app.state.model_service = model_service
    yield


app = FastAPI(title=API_TITLE, version=API_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_service(request: Request) -> TitanicModelService:
    return request.app.state.model_service


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for error in exc.errors():
        location = [str(part) for part in error.get("loc", ()) if part != "body"]
        details.append(
            {
                "field": ".".join(location) or "body",
                "message": error.get("msg", "Nilai tidak valid."),
                "type": error.get("type", "value_error"),
            }
        )
    return JSONResponse(
        status_code=422,
        content=error_body(
            "VALIDATION_ERROR",
            "Data penumpang tidak valid. Periksa kembali field yang ditandai.",
            details,
        ),
    )


@app.exception_handler(ModelUnavailableError)
async def model_unavailable_handler(request: Request, exc: ModelUnavailableError) -> JSONResponse:
    detail = {"message": str(exc)}
    if get_service(request).load_error:
        detail["load_error"] = get_service(request).load_error
    return JSONResponse(
        status_code=500,
        content=error_body("MODEL_NOT_LOADED", "Model machine learning belum tersedia.", [detail]),
    )


@app.exception_handler(PredictionError)
async def prediction_error_handler(request: Request, exc: PredictionError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_body("PREDICTION_FAILED", str(exc)),
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_body("INTERNAL_ERROR", "Terjadi kesalahan internal pada server.", [{"message": str(exc)}]),
    )


@app.get("/", tags=["Info"])
def root() -> dict:
    return {
        "api": API_TITLE,
        "version": API_VERSION,
        "endpoints": ["/api/health", "/api/predict"],
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health(request: Request) -> dict:
    status = get_service(request).health()
    return {**status, "api_version": API_VERSION}


@app.post("/api/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(payload: PassengerInput, request: Request) -> dict:
    return get_service(request).predict(payload)
