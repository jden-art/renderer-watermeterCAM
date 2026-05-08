FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage /app/data

# Changed from: CMD uvicorn main:app ...
# Using 'python -m uvicorn' is more reliable in slim containers
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
