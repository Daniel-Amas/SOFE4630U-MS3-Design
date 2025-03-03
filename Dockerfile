# Use an official Python image as the base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (including curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    curl \  
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Force reinstallation of ultralytics to ensure proper module loading
RUN pip uninstall -y ultralytics && pip install ultralytics

# Download the YOLOv8 model weights before running
RUN mkdir -p /app/models && \
    curl -L -o /app/models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt

# Copy the entire application folder into the container
COPY . .

# Set environment variables for Google Cloud authentication (if needed)
# ENV GOOGLE_APPLICATION_CREDENTIALS="/app/gcp-key.json"

# Command to run the application (this will be overridden when running Dataflow)
CMD ["python", "filter_pedestrians.py"]
