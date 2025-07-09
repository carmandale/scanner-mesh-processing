#!/bin/bash

# Scanner Environment Setup Script
# For M4 and other new machines that need Python environment setup
# This script creates scanner_env virtual environment with required packages

set -e  # Exit on any error

echo "=========================================="
echo "Scanner Environment Setup"
echo "=========================================="
echo ""

# Check if we're in the correct directory
if [ ! -f "runScriptAutomated.sh" ]; then
    echo "❌ ERROR: This script must be run from the groove-test directory"
    echo "   Expected to find runScriptAutomated.sh in current directory"
    echo "   Please cd to /Users/administrator/groove-test and run again"
    exit 1
fi

# Check if scanner_env already exists
if [ -d "scanner_env" ]; then
    echo "⚠️  scanner_env directory already exists"
    echo "   Would you like to:"
    echo "   1) Remove and recreate (recommended)"
    echo "   2) Skip setup (use existing)"
    echo "   3) Cancel"
    echo ""
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo "🗑️  Removing existing scanner_env..."
            rm -rf scanner_env
            ;;
        2)
            echo "✅ Using existing scanner_env"
            exit 0
            ;;
        3)
            echo "❌ Setup cancelled"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 is not installed or not in PATH"
    echo "   Please install Python 3 and try again"
    exit 1
fi

echo "🐍 Python version: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv scanner_env

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source scanner_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📋 Installing packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing packages manually..."
    
    # Install core packages
    echo "📦 Installing core packages..."
    pip install opencv-python>=4.5.0
    pip install mtcnn>=0.1.1
    pip install mediapipe>=0.8.0
    pip install tensorflow>=2.8.0
    
    # Install supporting packages
    echo "📦 Installing supporting packages..."
    pip install numpy>=1.21.0
    pip install pillow>=8.0.0
    pip install scipy>=1.7.0
    pip install colorama>=0.4.4
    pip install requests>=2.25.0
    pip install urllib3>=1.26.0
fi

echo ""
echo "🧪 Testing package imports..."

# Test critical packages
python3 -c "import cv2; print('✅ OpenCV version:', cv2.__version__)" || echo "❌ OpenCV import failed"
python3 -c "import mtcnn; print('✅ MTCNN imported successfully')" || echo "❌ MTCNN import failed"
python3 -c "import colorama; print('✅ Colorama imported successfully')" || echo "❌ Colorama import failed"
python3 -c "import mediapipe; print('✅ MediaPipe imported successfully')" || echo "❌ MediaPipe import failed"
python3 -c "import tensorflow; print('✅ TensorFlow version:', tensorflow.__version__)" || echo "❌ TensorFlow import failed"

# Deactivate virtual environment
deactivate

echo ""
echo "=========================================="
echo "✅ Scanner Environment Setup Complete!"
echo "=========================================="
echo ""
echo "The scanner_env virtual environment has been created with all required packages."
echo "The pipeline will automatically detect and use this environment when available."
echo ""
echo "To manually activate the environment:"
echo "  source scanner_env/bin/activate"
echo ""
echo "To test the pipeline:"
echo "  ./runScriptAutomated.sh <scan_id>"
echo "" 