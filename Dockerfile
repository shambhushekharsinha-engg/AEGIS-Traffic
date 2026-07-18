# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for OpenCV, PyTorch, YOLOv8, and audio/video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies manifests
COPY requirements-dev.txt /app/
COPY requirements.txt /app/
COPY dashboard/requirements.txt /app/dashboard-requirements.txt

# Install python dependencies
# We use requirements-dev.txt because it contains the full set of packages (including PyTorch, Ultralytics YOLOv8, Streamlit, etc.)
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy all project files into the container at /app
COPY . /app/

# Expose ports:
# 8000 for FastAPI backend
# 8501 for Streamlit frontend
EXPOSE 8000
EXPOSE 8501

# The CMD is set to run the FastAPI backend by default.
# This can be overridden in docker-compose.yml or docker run to run Streamlit or tests.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
