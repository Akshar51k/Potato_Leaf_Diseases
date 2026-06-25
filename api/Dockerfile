FROM python:3.10-slim

LABEL maintainer="akshar"
LABEL description="Potato Disease Classification API"

WORKDIR /app

# Install dependencies first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Environment defaults (can be overridden at runtime)
ENV MODEL_PATH=/app/models/potato_1.h5
ENV ALLOWED_ORIGINS=http://localhost,http://localhost:3000
ENV PORT=8000
ENV MAX_FILE_SIZE_MB=10

# Models will be mounted via docker-compose volume
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/ping')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
