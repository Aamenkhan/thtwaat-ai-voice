# Use NVIDIA CUDA base image for GPU support
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg is critical for moviepy, git for TTS models)
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Torch with CUDA 11.8 support
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install remaining Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the server source code
COPY ai_server/ ./ai_server/
COPY templates/ ./templates/
# static/ is created at runtime by the app
RUN mkdir -p /app/ai_server/static/images

# Environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Change to the server directory for runtime
WORKDIR /app/ai_server

# Expose the production port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
