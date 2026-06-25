"""
Potato Disease Classification API

A production-grade FastAPI service for classifying potato leaf diseases
using a pre-trained TensorFlow/Keras model.
"""

import logging
import os
from contextlib import asynccontextmanager
from io import BytesIO

from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

import numpy as np
import tensorflow as tf
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("potato-api")

# ---------------------------------------------------------------------------
# Environment Configuration
# ---------------------------------------------------------------------------
MODEL_PATH = os.getenv("MODEL_PATH", "../models/potato_1.h5")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost,http://localhost:3000"
).split(",")
PORT = int(os.getenv("PORT", "8000"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy", "Unknown"]

# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class PredictionResponse(BaseModel):
    """Schema for the /predict endpoint response."""

    class_name: str  # Serialized as 'class' via alias
    confidence: float

    class Config:
        # Allows the field to be populated by key 'class_name' internally
        # but serialized as 'class' in the JSON response for backward compat
        populate_by_name = True

    def dict(self, **kwargs):
        """Override to maintain backward-compatible 'class' key."""
        d = super().dict(**kwargs)
        d["class"] = d.pop("class_name")
        return d


class HealthResponse(BaseModel):
    """Schema for the /ping endpoint response."""

    status: str
    model_loaded: bool


# ---------------------------------------------------------------------------
# Model Lifecycle
# ---------------------------------------------------------------------------
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the ML model on startup; release on shutdown."""
    global model
    logger.info("Loading model from: %s", MODEL_PATH)
    try:
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        logger.info("Model loaded successfully.")
    except Exception:
        logger.exception("Failed to load model — predictions will be unavailable.")
    yield
    logger.info("Shutting down — releasing model resources.")
    model = None


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Potato Disease Classification API",
    description=(
        "Upload a potato leaf image and receive a disease classification "
        "(Early Blight, Late Blight, Healthy) with confidence score."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

origins = ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Core Helpers — UNCHANGED logic
# ---------------------------------------------------------------------------
def read_file_as_image(data) -> np.ndarray:
    image = Image.open(BytesIO(data))  # raw data to image
    image = image.resize((256, 256))  # resizing
    image = np.array(image)  # to numpy array
    return image


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/ping")
async def ping():
    return "Hello, I am alive"


@app.get("/health", response_model=HealthResponse)
async def health():
    """Extended health-check with model status."""
    return HealthResponse(status="ok", model_loaded=model is not None)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # --- guard: model availability ---
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please check server logs.",
        )

    # --- guard: file type ---
    extension = file.filename.split(".")[-1] in ("jpg", "jpeg")
    if not extension:
        return {"error": "File must be a jpg or jpeg image."}

    # --- guard: file size ---
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB.",
        )

    try:
        image = read_file_as_image(contents)

        img_batch = np.expand_dims(image, 0)  # batched input for model [[256, 256, 3]]

        predictions = model.predict(img_batch)

        predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
        confidence = np.max(predictions[0])

        logger.info(
            "Predicted class: %s, Confidence: %.4f", predicted_class, confidence
        )
        return {
            "class": predicted_class,
            "confidence": float(confidence),
        }

    except Exception:
        logger.exception("Prediction failed for file: %s", file.filename)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during prediction.",
        )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=PORT)