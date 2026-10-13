# Multi-stage Dockerfile for SilicaForge-RL SCADA Digital Twin
# Stage 1: Build the React 19 + Three.js production frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python 3.11 FastAPI backend with PyTorch & Stable-Baselines3
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, models, and configuration
COPY src/ ./src/
COPY data/ ./data/
COPY best_model.zip config.json ./
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["python", "src/web/app.py"]
