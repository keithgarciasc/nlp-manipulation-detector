"""
FastAPI Inference Service for NLP Manipulation Detector

Production-ready inference API for detecting manipulative language in text.
Loads a fine-tuned DistilBERT model at startup and provides a /predict endpoint.

Usage:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model configuration
MODEL_PATH = Path("../models/manipulation_detector_model")
MAX_INPUT_LENGTH = 512  # DistilBERT max sequence length
MIN_INPUT_LENGTH = 3    # Minimum meaningful input

# Label mapping
LABEL_MAP = {
    0: "neutral",
    1: "manipulative"
}

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL MODEL STATE
# ============================================================================

class ModelState:
    """Global container for loaded model and tokenizer."""
    tokenizer = None
    model = None
    device = None


model_state = ModelState()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PredictionRequest(BaseModel):
    """Request schema for text classification."""

    text: str = Field(
        ...,
        description="Input text to classify",
        min_length=MIN_INPUT_LENGTH,
        max_length=MAX_INPUT_LENGTH * 4  # Approximate character limit
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and clean input text."""
        # Strip whitespace
        v = v.strip()

        # Check minimum length
        if len(v) < MIN_INPUT_LENGTH:
            raise ValueError(
                f"Text must be at least {MIN_INPUT_LENGTH} characters long"
            )

        # Check for empty or whitespace-only input
        if not v or v.isspace():
            raise ValueError("Text cannot be empty or whitespace only")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "SHOCKING: Economy in COMPLETE MELTDOWN!"
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Response schema for text classification."""

    label: str = Field(
        ...,
        description="Predicted label: 'neutral' or 'manipulative'"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "label": "manipulative",
                    "confidence": 0.87
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str
    model_loaded: bool
    device: str


# ============================================================================
# LIFECYCLE MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.

    Loads model and tokenizer at startup, cleans up at shutdown.
    """
    # Startup: Load model and tokenizer
    logger.info("Starting up: Loading model and tokenizer...")

    try:
        # Set device (CPU only as per requirements)
        model_state.device = torch.device("cpu")
        logger.info(f"Using device: {model_state.device}")

        # Load tokenizer
        logger.info(f"Loading tokenizer from {MODEL_PATH}")
        model_state.tokenizer = AutoTokenizer.from_pretrained(
            "distilbert-base-uncased"
        )

        # Load model
        logger.info(f"Loading model from {MODEL_PATH}")
        model_state.model = AutoModelForSequenceClassification.from_pretrained(
            str(MODEL_PATH)
        )

        # Move model to device and set to eval mode
        model_state.model.to(model_state.device)
        model_state.model.eval()

        logger.info("Model and tokenizer loaded successfully")
        logger.info(f"Model parameters: {sum(p.numel() for p in model_state.model.parameters()):,}")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")

    # Application is running
    yield

    # Shutdown: Cleanup
    logger.info("Shutting down: Cleaning up resources...")
    model_state.model = None
    model_state.tokenizer = None
    logger.info("Shutdown complete")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="NLP Manipulation Detector API",
    description="Inference API for detecting manipulative language in text using fine-tuned DistilBERT",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "NLP Manipulation Detector API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the current status of the API and whether the model is loaded.
    """
    return {
        "status": "healthy" if model_state.model is not None else "unhealthy",
        "model_loaded": model_state.model is not None,
        "device": str(model_state.device) if model_state.device else "unknown"
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest):
    """
    Predict whether input text is manipulative or neutral.

    Args:
        request: PredictionRequest containing text to classify

    Returns:
        PredictionResponse with label and confidence score

    Raises:
        HTTPException: If model is not loaded or inference fails
    """
    # Check if model is loaded
    if model_state.model is None or model_state.tokenizer is None:
        logger.error("Prediction attempted but model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please try again later."
        )

    try:
        # Log request (without full text for privacy)
        logger.info(f"Prediction request received (text length: {len(request.text)} chars)")

        # Tokenize input
        inputs = model_state.tokenizer(
            request.text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=MAX_INPUT_LENGTH
        )

        # Move inputs to device
        inputs = {k: v.to(model_state.device) for k, v in inputs.items()}

        # Run inference (no gradient computation needed)
        with torch.no_grad():
            outputs = model_state.model(**inputs)
            logits = outputs.logits

            # Get prediction and confidence
            probabilities = torch.softmax(logits, dim=-1)
            confidence, predicted_class = torch.max(probabilities, dim=-1)

            # Convert to Python types
            predicted_class = predicted_class.item()
            confidence = confidence.item()

        # Map prediction to label
        label = LABEL_MAP.get(predicted_class, "unknown")

        # Log result
        logger.info(f"Prediction: {label} (confidence: {confidence:.4f})")

        return PredictionResponse(
            label=label,
            confidence=round(confidence, 4)
        )

    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn programmatically
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    )
