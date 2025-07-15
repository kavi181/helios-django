# Use stable Python
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    curl \
    tesseract-ocr \
 && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy project
COPY . /app/

# Install pip + requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Start command
CMD gunicorn helios.wsgi:application --bind 0.0.0.0:$PORT
