# ── Stage 1: Build & Dependency Installation ─────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies needed for compiling python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install via pip wheel
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# ── Stage 2: Final Light Runtime Container ────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies (like postgres library client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled wheels from builder stage
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

# Setup non-root security group and user
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/bash appuser

# Copy application files and grant permissions
COPY --chown=appuser:appgroup . .

# Expose standard container port
EXPOSE 8000

# Switch context to the non-root user
USER appuser

# Define application startup command using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
