FROM python:3.10-slim

LABEL maintainer="Phelomia Team"
LABEL description="Phelomia - AI-Powered Document Analysis & Conversion"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs assets/uploads data/images

# Set environment variables
ENV PYTHONPATH=/app
ENV PHELOMIA_DEVICE=cpu
ENV PHELOMIA_THEME=carbon

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application
CMD ["python", "src/app.py"]