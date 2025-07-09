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
    echo "❌ ERROR: This script must be run from the directory containing runScriptAutomated.sh"
    echo "   Expected to find runScriptAutomated.sh in current directory"
    echo "   Please cd to the directory containing runScriptAutomated.sh and run again"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Check if scanner_env already exists
if [ -d "scanner_env" ]; then
    echo "⚠️  scanner_env directory already exists"
    echo "   Would you like to:"
    echo "   1) Remove and recreate (recommended)"
    echo "   2) Skip setup (use existing)"
    echo "   3) Use working environment from parent directory"
    echo "   4) Cancel"
    echo ""
    read -p "Enter choice (1-4): " choice
    
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
            WORKING_ENV="../scanner_env"
            if [ -d "$WORKING_ENV" ]; then
                echo "🔗 Creating symlink to working environment..."
                rm -rf scanner_env
                ln -s "$WORKING_ENV" scanner_env
                echo "✅ Linked to working environment"
                exit 0
            else
                echo "❌ Working environment not found at $WORKING_ENV"
                exit 1
            fi
            ;;
        4)
            echo "❌ Setup cancelled"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

# Check if Python 3 is available and find compatible version
PYTHON_CMD=""
PYTHON_VERSION=""

# Try to find Python 3.12 first (known to work with mediapipe)
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    PYTHON_VERSION=$(python3.12 --version)
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    PYTHON_VERSION=$(python3.11 --version)
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    PYTHON_VERSION=$(python3.10 --version)
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    
    # Check if Python 3.13+ and warn about mediapipe compatibility
    if python3 -c "import sys; exit(0 if sys.version_info < (3, 13) else 1)" 2>/dev/null; then
        echo "✅ Python version compatible: $PYTHON_VERSION"
    else
        echo "⚠️  Python version: $PYTHON_VERSION"
        echo "   WARNING: Python 3.13+ may have compatibility issues with mediapipe"
        echo "   Consider using Python 3.12 if available (python3.12)"
        echo "   Continue anyway? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "❌ Setup cancelled"
            exit 1
        fi
    fi
else
    echo "❌ ERROR: No compatible Python version found"
    echo "   Please install Python 3.10, 3.11, or 3.12"
    exit 1
fi

echo "🐍 Using Python: $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv scanner_env

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