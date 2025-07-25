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

# ========================================
# Xcode Command Line Tools Installation
# ========================================
echo "🔧 Installing Xcode Command Line Tools..."
chmod +x install-xcode.sh
./install-xcode.sh

# ========================================
# Blender Installation
# ========================================
echo "🎨 Setting up Blender..."
echo ""

# Check if Blender is already installed
if [ -d "/Applications/Blender.app" ]; then
    echo "✅ Blender is already installed"
    BLENDER_VERSION=$(/Applications/Blender.app/Contents/MacOS/Blender --version 2>/dev/null | head -1 || echo "Unknown version")
    echo "   Version: $BLENDER_VERSION"
else
    echo "📦 Blender not found. Installing Blender 3.5.1..."
    echo ""
    
    # Download Blender for macOS ARM64
    echo "⬇️  Downloading Blender 3.5.1 for macOS ARM64..."
    curl -O https://download.blender.org/release/Blender3.5/blender-3.5.1-macos-arm64.dmg
    
    # Mount the DMG
    echo "📁 Mounting Blender DMG..."
    hdiutil attach blender-3.5.1-macos-arm64.dmg
    
    # Copy Blender to Applications
    echo "📂 Installing Blender to /Applications..."
    sudo cp -rf /Volumes/Blender/Blender.app /Applications
    
    # Unmount the DMG
    echo "🗑️  Cleaning up..."
    hdiutil detach /Volumes/Blender
    rm -f blender-3.5.1-macos-arm64.dmg
    
    # Verify installation
    if [ -d "/Applications/Blender.app" ]; then
        echo "✅ Blender installed successfully"
        /Applications/Blender.app/Contents/MacOS/Blender --help > /dev/null 2>&1 || echo "⚠️  Blender may need additional setup"
    else
        echo "❌ Blender installation failed"
        exit 1
    fi
fi

echo ""

# ========================================
# Python Environment Setup
# ========================================

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

# macOS: ensure Python 3.11 is installed via Homebrew
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v python3.11 &> /dev/null; then
        echo "🔧 Installing Python 3.11 via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "🍺 Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            # Configure Homebrew environment
            eval "$(/opt/homebrew/bin/brew shellenv)" || eval "$(/usr/local/bin/brew shellenv)"
        fi
        brew install python@3.11
        brew link --force python@3.11
    fi
fi

# Only Python 3.11 is supported
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    PYTHON_VERSION=$(python3.11 --version)
else
    echo "❌ ERROR: Python 3.11 is required. Please install Python 3.11"
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
echo "Setup completed successfully:"
echo "  • Xcode Command Line Tools installed"
echo "  • Blender 3.5.1 installed to /Applications"
echo "  • scanner_env virtual environment created with all required packages"
echo ""
echo "The pipeline will automatically detect and use this environment when available."
echo ""
echo "To manually activate the environment:"
echo "  source scanner_env/bin/activate"
echo ""
echo "To test the pipeline:"
echo "  ./runScriptAutomated.sh <scan_id>"
echo "" 
# Line endings standardized to LF 