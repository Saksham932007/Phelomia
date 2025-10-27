#!/bin/bash

# Phelomia Quick Start Script
echo "🚀 Starting Phelomia..."

# Check if virtual environment exists
if [ ! -d "phelomia_env" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate virtual environment and start the application
source phelomia_env/bin/activate
echo "Starting Phelomia Document AI Platform..."
python src/app.py