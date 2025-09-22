# --- Stage 1: Build dependencies ---
FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build tools for psycopg2 / Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
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
RUN pip install --no-cache-dir /wheels/*

# Copy all project files
COPY . .

# Copy scripts explicitly
COPY entrypoint.sh /app/entrypoint.sh
COPY migrate.sh /app/migrate.sh

# Make scripts executable
RUN chmod +x /app/migrate.sh /app/entrypoint.sh

# Expose Django default port
EXPOSE 8888

# Default command
CMD ["/app/entrypoint.sh"]


