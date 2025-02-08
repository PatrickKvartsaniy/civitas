# Use a minimal Python 3.9 image
FROM python:3.9-slim

# Set environment variable to disable output buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Install system dependencies and Python dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

CMD ["python", "main.py", "web"]
