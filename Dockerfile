FROM node:24-bookworm-slim AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml requirements.txt README.md ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY backend/ backend/
COPY ml/ ml/
COPY scrapers/ scrapers/
COPY scripts/ scripts/
COPY data/seed/ data/seed/
COPY --from=frontend /frontend/dist/ frontend/dist/
# Browser scraping is an optional deployment profile; API/roster work on arm64 and amd64.
RUN mkdir -p data/processed && python -m scripts.seed_data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
