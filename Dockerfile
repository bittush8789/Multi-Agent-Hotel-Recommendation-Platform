# Multi-stage production-grade Dockerfile for TravelMind AI

# --- Base Image with Shared Security Configurations ---
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

# Install common system dependencies securely
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root group and user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser

# --- Backend Target Stage ---
FROM base AS backend

# Copy and install dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ ./

# Create default SQLite db file and chroma directory with ownership by appuser
RUN touch travelmind.db && \
    mkdir -p chroma_db && \
    chown -R appuser:appgroup /workspace

# Switch to non-root user
USER 10001

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# --- Frontend Target Stage ---
FROM base AS frontend

# Copy and install dependencies
COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY frontend/ ./

# Set ownership
RUN chown -R appuser:appgroup /workspace

# Switch to non-root user
USER 10001

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8501/ || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
