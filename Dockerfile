# Production Dockerfile for SilicaForge-RL SCADA Digital Twin & PPO Backend
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, models, configuration, and pre-built UI
COPY src/ ./src/
COPY data/ ./data/
COPY best_model.zip config.json ./
COPY frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["python", "src/web/app.py"]
