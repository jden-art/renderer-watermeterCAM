FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-create directories so they have correct permissions
RUN mkdir -p /app/storage /app/data

# Render sets the PORT env variable automatically
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
