#!/bin/bash

# Xcode Command Line Tools Installation Script
# Checks if Xcode command line tools are installed and installs them if needed

set -e  # Exit on any error

echo "=========================================="
echo "Xcode Command Line Tools Setup"
echo "=========================================="
echo ""

# Check if Xcode command line tools are already installed
if xcode-select -p &> /dev/null; then
    echo "✅ Xcode command line tools are already installed"
    echo "   Installation path: $(xcode-select -p)"
    echo ""
    
    # Verify installation by checking for common tools
    if command -v gcc &> /dev/null && command -v make &> /dev/null; then
        echo "✅ Development tools verified: gcc, make found"
    else
        echo "⚠️  Development tools may be incomplete"
    fi
else
    echo "📦 Xcode command line tools not found. Installing..."
    echo ""
    
    # Install Xcode command line tools
    echo "🔧 Running: xcode-select --install"
    echo "   A dialog will appear - please click 'Install' to proceed"
    echo "   This may take several minutes..."
    
    xcode-select --install
    
    echo ""
    echo "⏳ Waiting for installation to complete..."
    echo "   Please complete the installation dialog and press Enter when finished"
    read -p "Press Enter to continue after installation completes..."
    
    # Verify installation
    if xcode-select -p &> /dev/null; then
        echo "✅ Xcode command line tools installed successfully"
        echo "   Installation path: $(xcode-select -p)"
    else
        echo "❌ Xcode command line tools installation failed"
        echo "   Please install manually: xcode-select --install"
        exit 1
    fi
fi

echo ""
echo "✅ Xcode Command Line Tools Setup Complete!"
echo ""
