# Multi-stage Dockerfile for Universal Multimodal RAG Assistant

FROM python:3.12-slim as backend-builder

WORKDIR /app

# Install system dependencies for PyMuPDF and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmupdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY dataset/ /app/dataset/

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
