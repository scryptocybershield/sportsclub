# docker/app/Dockerfile
FROM python:3.13-slim-trixie
EXPOSE 8080

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

# Copy project
COPY sportsclub/ .

# Collect static files (needed when serving through a reverse proxy)
RUN python manage.py collectstatic --noinput

# Create non-privileged user for security
RUN useradd --create-home --shell /bin/bash appuser

# Change ownership of application directory
RUN chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

# Run uvicorn as non-privileged user
CMD ["uvicorn", "sportsclub.asgi:application", "--host", "0.0.0.0", "--port", "8080"]
