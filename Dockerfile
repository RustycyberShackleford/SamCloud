# Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Render/Heroku will provide PORT; default for local docker runs
ENV PORT=8080

# Start via Gunicorn, binding to $PORT
CMD ["gunicorn", "app:app", "--preload", "-b", "0.0.0.0:${PORT}"]
