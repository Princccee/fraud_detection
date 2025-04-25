# Use an official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Copy requirement file first to leverage Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . /app

# Expose Django port
EXPOSE 8000

# Default command: run Gunicorn server
CMD ["gunicorn", "fraud_detection.wsgi:application", "--bind", "0.0.0.0:8000"]
