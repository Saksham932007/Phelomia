# Performance optimization tips and monitoring guide

# Memory Usage Optimization
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export TRANSFORMERS_CACHE=/app/.cache/transformers
export HF_HOME=/app/.cache/huggingface

# Production Environment Variables
export PHELOMIA_DEVICE=auto
export PHELOMIA_BATCH_SIZE=1
export PHELOMIA_MAX_LENGTH=1024
export PHELOMIA_CACHE_ENABLED=true
export PHELOMIA_DEBUG=false
export PHELOMIA_LOG_LEVEL=INFO

# GPU Optimization (if available)
export CUDA_VISIBLE_DEVICES=0
export NVIDIA_VISIBLE_DEVICES=all

# Resource Limits for Docker
# --memory=4g --cpus=2.0 --memory-swap=8g

# Monitoring Commands
echo "System Resource Usage:"
echo "====================="

# Memory usage
echo "Memory Usage:"
free -h

# CPU usage
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4"%"}'

# Disk usage
echo "Disk Usage:"
df -h

# GPU usage (if available)
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Usage:"
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits
fi

# Docker container stats (if running in Docker)
if [ -f /.dockerenv ]; then
    echo "Container Stats:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
fi

# Application-specific metrics
echo "Application Metrics:"
echo "==================="

# Check if Phelomia is running
if curl -f http://localhost:7860/health > /dev/null 2>&1; then
    echo "✅ Phelomia is running"
    
    # Get application metrics
    curl -s http://localhost:7860/metrics 2>/dev/null | head -10
else
    echo "❌ Phelomia is not responding"
fi

# Log file sizes
echo "Log File Sizes:"
find logs/ -name "*.log" -exec ls -lh {} \; 2>/dev/null || echo "No log files found"

# Cache sizes
echo "Cache Sizes:"
du -sh .cache/ 2>/dev/null || echo "No cache directory found"

# Database size (if applicable)
echo "Storage Usage:"
du -sh data/ results/ 2>/dev/null || echo "No data directories found"