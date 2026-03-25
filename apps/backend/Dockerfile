# Use an optimized Python image
FROM python:3.11-slim

# Install system dependencies for build and networking
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade protobuf grpcio grpcio-tools

# Install Ollama (for hosting local LLMs)
# This will download and install the Ollama binary
# For GPU support, a different base image and installation method would be required.
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy the application code
COPY . .

# Compile gRPC definitions
RUN python -m grpc_tools.protoc -I. --python_out=./app --grpc_python_out=./app proto/a2a.proto

# Expose gRPC and Dashboard ports
EXPOSE 50051 8080

# Start the orchestrator server
CMD ["python", "-u", "main.py", "serve"]
