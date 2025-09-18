# --- Stage 1: Build stage ---
FROM python:3.12-slim as builder

WORKDIR /usr/src/app

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Copy requirements and install wheels. No system dependencies needed for psycopg2-binary.
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Stage 2: Final stage ---
FROM python:3.12-slim

WORKDIR /usr/src/app

# Copy installed wheels from the builder stage
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy the entire project into the image
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8000

# The command to run the application (ensure project name is correct)
CMD ["gunicorn", "savannah_assess.wsgi:application", "--bind", "0.0.0.0:8000"]
