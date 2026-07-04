# ---------- Base image ----------
FROM python:3.12-slim

# ---------- Environment ----------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    UV_CACHE_DIR=/tmp/uv-cache

# ---------- System deps ----------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
    && rm -rf /var/lib/apt/lists/*

# ---------- Install uv ----------
RUN pip install --no-cache-dir uv

# ---------- Workdir ----------
WORKDIR /app

# ---------- Copy dependency files first (cache-friendly) ----------
COPY pyproject.toml uv.lock ./

# ---------- Install dependencies ----------
RUN uv sync --frozen --no-dev

# ---------- Copy application ----------
COPY src ./src

# ---------- Expose port (adjust if needed) ----------
EXPOSE 8000

# ---------- Run backend ----------
CMD ["uv", "run", "src/app/main.py"]