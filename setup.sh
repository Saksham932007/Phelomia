#!/bin/bash

# Phelomia Setup Script
# Automated setup for Phelomia Document AI Platform

set -e

echo "🚀 Setting up Phelomia Document AI Platform..."
echo "================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
    major_version=$(echo $python_version | cut -d. -f1)
    minor_version=$(echo $python_version | cut -d. -f2)
    
    if [ "$major_version" -ge 3 ] && [ "$minor_version" -ge 8 ]; then
        print_success "Python $python_version detected ✓"
    else
        print_error "Python 3.8+ required. Current: $python_version"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment already exists
if [ -d "phelomia_env" ]; then
    print_warning "Virtual environment already exists. Removing old environment..."
    rm -rf phelomia_env
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv phelomia_env
print_success "Virtual environment created ✓"

# Activate virtual environment
print_status "Activating virtual environment..."
source phelomia_env/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
print_status "Installing dependencies (this may take a few minutes)..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_success "Dependencies installed ✓"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating default configuration file..."
    cat > .env << EOF
# Phelomia Configuration
PHELOMIA_DEVICE=auto
PHELOMIA_THEME=carbon
PHELOMIA_ENABLE_CHAT=true
PHELOMIA_MAX_FILE_SIZE=10
PHELOMIA_BATCH_SIZE=1
PHELOMIA_CACHE_ENABLED=true
PHELOMIA_DEBUG=false
EOF
    print_success "Configuration file created ✓"
fi

# Create logs directory
mkdir -p logs
print_success "Logs directory created ✓"

# Create assets directory for user uploads
mkdir -p assets/uploads
print_success "Assets directory created ✓"

echo ""
echo "================================================"
print_success "Setup complete! 🎉"
echo ""
echo "To start Phelomia:"
echo "  1. source phelomia_env/bin/activate"
echo "  2. python src/app.py"
echo ""
echo "Or run: ./start.sh"
echo "================================================"