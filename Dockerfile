# Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default (for local docker run); Render supplies PORT at runtime
ENV PORT=8080

# Use shell form so $PORT expands correctly on Render
CMD gunicorn app:app --preload -b 0.0.0.0:$PORT
