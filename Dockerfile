FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p output
ENV PYTHONUNBUFFERED=1
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 --access-logfile - app:app
