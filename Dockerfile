# Hugging Face Spaces Dockerfile
# Runs both FastAPI backend and Streamlit frontend in one container

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY ui/ ./ui/
COPY models/ ./models/

# Create startup script that runs both services
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting FastAPI backend..."\n\
cd /app/api && uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
API_PID=$!\n\
\n\
echo "Waiting for API to start..."\n\
sleep 8\n\
\n\
echo "Starting Streamlit frontend..."\n\
cd /app/ui && streamlit run app.py --server.port 7860 --server.address 0.0.0.0 --server.headless true &\n\
STREAMLIT_PID=$!\n\
\n\
echo "Both services started"\n\
echo "API PID: $API_PID"\n\
echo "Streamlit PID: $STREAMLIT_PID"\n\
\n\
# Wait for both processes\n\
wait -n\n\
\n\
# Exit with status of process that exited first\n\
exit $?\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port 7860 (Hugging Face Spaces requirement)
EXPOSE 7860

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:7860/_stcore/health || exit 1

# Run startup script
CMD ["/app/start.sh"]
