FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# create media directory and set appropriate permissions
RUN mkdir -p files/media \
 && adduser --disabled-password --no-create-home django-user \
 && chown -R django-user:django-user files/media \
 && chmod -R 755 files/media

USER django-user
