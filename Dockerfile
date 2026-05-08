FROM python:3.11-slim

WORKDIR /app

# Cache-buster: change this number if you need to force re-install later
ENV RENDER_CACHE_BUST=2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage /app/data

CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
