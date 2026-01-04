# NLP Manipulation Detector - FastAPI Inference Service

Production-ready REST API for detecting manipulative language in text using a fine-tuned DistilBERT model.

## Quick Start

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# From the api directory
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 3. Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "message": "NLP Manipulation Detector API",
  "version": "1.0.0",
  "endpoints": {
    "predict": "/predict (POST)",
    "health": "/health (GET)",
    "docs": "/docs (GET)"
  }
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

### `POST /predict`
Classify text as manipulative or neutral.

**Request:**
```json
{
  "text": "SHOCKING: Economy in COMPLETE MELTDOWN!"
}
```

**Response:**
```json
{
  "label": "manipulative",
  "confidence": 0.8734
}
```

## Usage Examples

### cURL

```bash
# Predict
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "SHOCKING: Economy in COMPLETE MELTDOWN!"}'

# Health check
curl "http://localhost:8000/health"
```

### Python (requests)

```python
import requests

# Make prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "SHOCKING: Economy in COMPLETE MELTDOWN!"}
)

result = response.json()
print(f"Label: {result['label']}")
print(f"Confidence: {result['confidence']}")
```

### Python (httpx - async)

```python
import httpx
import asyncio

async def predict(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/predict",
            json={"text": text}
        )
        return response.json()

# Run prediction
result = asyncio.run(predict("Breaking: New policy announced"))
print(result)
```

### JavaScript (fetch)

```javascript
// Make prediction
fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'SHOCKING: Economy in COMPLETE MELTDOWN!'
  })
})
  .then(response => response.json())
  .then(data => {
    console.log('Label:', data.label);
    console.log('Confidence:', data.confidence);
  });
```

## Input Validation

The API validates input with the following rules:

- **Minimum length**: 3 characters
- **Maximum length**: 512 tokens (approximately 2,048 characters)
- **Non-empty**: Cannot be empty or whitespace-only
- **Type**: Must be a string

### Error Responses

**400 Bad Request** - Invalid input:
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "Text must be at least 3 characters long",
      "type": "value_error"
    }
  ]
}
```

**503 Service Unavailable** - Model not loaded:
```json
{
  "detail": "Model not loaded. Please try again later."
}
```

**500 Internal Server Error** - Inference failure:
```json
{
  "detail": "Prediction failed: <error message>"
}
```

## Configuration

Edit the configuration section in [main.py](main.py):

```python
# Model configuration
MODEL_PATH = Path("../models/manipulation_detector_model")
MAX_INPUT_LENGTH = 512  # DistilBERT max sequence length
MIN_INPUT_LENGTH = 3    # Minimum meaningful input

# Label mapping
LABEL_MAP = {
    0: "neutral",
    1: "manipulative"
}
```

## Production Deployment

### Using Gunicorn + Uvicorn Workers

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Environment Variables

```bash
# Set host and port
export API_HOST=0.0.0.0
export API_PORT=8000

# Run
uvicorn main:app --host $API_HOST --port $API_PORT
```

### Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Copy model (or mount as volume)
COPY ../models/manipulation_detector_model ./models/manipulation_detector_model

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t manipulation-detector-api .
docker run -p 8000:8000 manipulation-detector-api
```

## Performance Considerations

### Startup Time
- Model loading takes ~2-5 seconds on CPU
- Model is loaded once at startup (not per request)

### Inference Latency
- CPU inference: ~50-200ms per request (depending on input length)
- Single request processing (no batching)

### Memory Usage
- Model: ~250MB RAM
- Base overhead: ~100MB
- Total: ~350-400MB per worker

### Scaling Recommendations
- Use multiple Uvicorn workers for concurrent requests
- Recommended: 2-4 workers per CPU core
- For GPU: use single worker with batch processing (not included)

## Logging

Logs are written to stdout with the following format:
```
2024-01-04 10:23:45,123 - __main__ - INFO - Prediction request received (text length: 45 chars)
2024-01-04 10:23:45,234 - __main__ - INFO - Prediction: manipulative (confidence: 0.8734)
```

To save logs to file:
```bash
uvicorn main:app --log-config logging.json
```

## Monitoring

### Health Check Endpoint

Use `/health` for:
- Load balancer health checks
- Kubernetes liveness/readiness probes
- Monitoring systems (Prometheus, etc.)

Example health check script:
```bash
#!/bin/bash
response=$(curl -s http://localhost:8000/health)
status=$(echo $response | jq -r '.status')

if [ "$status" = "healthy" ]; then
  exit 0
else
  exit 1
fi
```

## Troubleshooting

### Model Not Loading

**Error**: `Model loading failed: <error>`

**Solutions**:
1. Verify model path is correct: `../models/manipulation_detector_model`
2. Check model files exist: `config.json` and `model.safetensors`
3. Ensure model is compatible with transformers version

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Use different port
uvicorn main:app --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows
```

### High Memory Usage

**Solutions**:
1. Reduce number of workers
2. Use CPU-only mode (default)
3. Enable model quantization (requires code changes)

## Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test prediction with neutral text
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Government announces new infrastructure plan"}'

# Test prediction with manipulative text
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "SHOCKING CRISIS: Everything is FALLING APART!"}'
```

### Load Testing (Optional)

Using `locust`:
```python
from locust import HttpUser, task, between

class ManipulationDetectorUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def predict(self):
        self.client.post("/predict", json={
            "text": "This is a test headline"
        })
```

## API Client Libraries

### Python Client Example

Create a reusable client:

```python
# client.py
import requests
from typing import Dict

class ManipulationDetectorClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def predict(self, text: str) -> Dict[str, any]:
        """Classify text as manipulative or neutral."""
        response = self.session.post(
            f"{self.base_url}/predict",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, any]:
        """Check API health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage
client = ManipulationDetectorClient()
result = client.predict("Breaking news about economy")
print(f"Label: {result['label']}, Confidence: {result['confidence']}")
```

## License

MIT License - See main project LICENSE file.

## Support

For issues or questions:
1. Check the [main project README](../README.md)
2. Review API documentation at `/docs`
3. Open an issue on GitHub
