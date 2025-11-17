#!/bin/bash

# GovContracts Pro - Automated Setup Script
# This script automates the installation and initial setup of the DaaS platform

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emojis
CHECK="✅"
CROSS="❌"
ROCKET="🚀"
GEAR="⚙️"
DATABASE="🗄️"
PYTHON="🐍"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              🏛️  GovContracts Pro Setup                      ║"
echo "║           Data-as-a-Service Contract Aggregator             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_step() {
    echo -e "\n${BLUE}${GEAR} $1${NC}"
}

# Check Python version
print_step "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.9+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
print_step "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Install dependencies
print_step "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_status "Dependencies installed"

# Install Playwright browsers
print_step "Installing Playwright browsers..."
if python -m playwright install chromium > /dev/null 2>&1; then
    print_status "Playwright Chromium installed"
else
    print_warning "Playwright installation might need manual setup"
    echo "Run: playwright install chromium"
fi

# Create necessary directories
print_step "Creating data directories..."
mkdir -p data
mkdir -p logs
print_status "Directories created"

# Setup environment file
print_step "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status ".env file created from template"
    print_warning "Please edit .env file with your configuration"
else
    print_warning ".env file already exists"
fi

# Initialize database
print_step "Initializing database and default data sources..."
python setup_sources.py
print_status "Database initialized with default sources"

# Final instructions
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    ${ROCKET} Setup Complete! ${ROCKET}                      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. ${GEAR}  Review and update configuration:"
echo "      nano .env"
echo ""
echo "2. ${ROCKET} Start the API Server:"
echo "      source venv/bin/activate"
echo "      python run_api.py"
echo ""
echo "3. ${GEAR}  Start the Scraper Scheduler (in new terminal):"
echo "      source venv/bin/activate"
echo "      python run_scraper.py"
echo ""
echo "4. ${DATABASE} Access the application:"
echo "      • Web Portal: http://localhost:8000/portal"
echo "      • API Docs:   http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}⚠️  Important: Change the default admin password!${NC}"
echo "   Default credentials: admin@govcontracts.pro / admin123"
echo ""
echo -e "${GREEN}Happy Contract Hunting! 🎯${NC}"
