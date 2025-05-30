# Use Python 3.11 slim image
FROM python:3.11-slim

# Add metadata labels
LABEL maintainer="NetWise Team"
LABEL description="NetWise Telegram Bot"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 netwise
USER netwise

# Command to run the application
CMD ["python", "main.py"] 