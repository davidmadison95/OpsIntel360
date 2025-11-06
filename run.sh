#!/bin/bash

# OpsIntel360 - Run Script
# Executes the complete pipeline and launches the dashboard

echo "=========================================="
echo "  OpsIntel360 - Setup & Launch Script"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

print_status "Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
print_info "Installing dependencies..."
pip install -q -r requirements.txt
print_status "Dependencies installed"

# Generate data
print_info "Generating synthetic data..."
python generate_data.py
if [ $? -eq 0 ]; then
    print_status "Data generation complete"
else
    print_error "Data generation failed"
    exit 1
fi

# Run ETL pipeline
print_info "Running ETL pipeline..."
python etl/etl_pipeline.py
if [ $? -eq 0 ]; then
    print_status "ETL pipeline complete"
else
    print_error "ETL pipeline failed"
    exit 1
fi

# Generate forecasts
print_info "Generating forecasts..."
python models/forecasting.py
print_status "Forecasting complete"

# Detect anomalies
print_info "Detecting anomalies..."
python models/anomalies.py
print_status "Anomaly detection complete"

# Generate insights
print_info "Generating insights..."
python models/insights.py
print_status "Insight generation complete"

echo ""
echo "=========================================="
echo "  Setup Complete! Launching Dashboard..."
echo "=========================================="
echo ""
print_info "Dashboard will be available at: http://localhost:8501"
echo ""

# Launch Streamlit dashboard
streamlit run app/dashboard_app.py
