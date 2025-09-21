# --- Stage 1: Build dependencies ---
FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

# Prevent writing pyc files and unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build tools for psycopg2 / Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Stage 2: Final image ---
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels and install them
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy project code
COPY . .

# Make scripts executable
RUN chmod +x /app/migrate.sh /app/entrypoint.sh

# Expose default port
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["/app/entrypoint.sh"]


