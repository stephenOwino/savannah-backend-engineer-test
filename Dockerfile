# --- Stage 1: Build dependencies ---
FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

# Prevent writing pyc files and unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Final image ---
FROM python:3.12-slim

WORKDIR /app

# Copy pre-built wheels and install them
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy project code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose default port
EXPOSE 8000

# Run the entrypoint
CMD ["/app/entrypoint.sh"]

