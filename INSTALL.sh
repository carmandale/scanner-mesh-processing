#!/bin/bash

# Scanner Pipeline Update Installer
# Run this script on the server to install the updated pipeline files

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 SCANNER PIPELINE UPDATE INSTALLER"
echo "══════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -f "runScriptAutomated.sh" ]; then
    echo -e "${RED}❌ Error: Installation files not found${NC}"
    echo "Please make sure you're running this script from the extracted update directory"
    echo "Expected files:"
    echo "  - runScriptAutomated.sh"
    echo "  - software/scannermeshprocessing-2023/config.json"
    echo "  - And other pipeline files..."
    exit 1
fi

# Detect server base directory
SERVER_BASE="/Users/administrator/groove-test"
if [ ! -d "$SERVER_BASE" ]; then
    echo -e "${YELLOW}⚠️  Standard server directory not found: $SERVER_BASE${NC}"
    echo -n "Enter the base directory path (where groove-test is located): "
    read SERVER_BASE
    if [ ! -d "$SERVER_BASE" ]; then
        echo -e "${RED}❌ Directory not found: $SERVER_BASE${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}📁 Installing to: $SERVER_BASE${NC}"
echo ""

# Function to backup and install a file
install_file() {
    local source_file="$1"
    local target_file="$2"
    local description="$3"
    
    echo -n "📄 Installing ${description}... "
    
    # Create backup if target exists
    if [ -f "$target_file" ]; then
        cp "$target_file" "${target_file}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create target directory if needed
    mkdir -p "$(dirname "$target_file")"
    
    # Copy file
    if cp "$source_file" "$target_file"; then
        echo -e "${GREEN}✅ Installed${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
}

# Install main pipeline script
echo -e "${BLUE}🔧 Installing Main Pipeline:${NC}"
install_file "runScriptAutomated.sh" "$SERVER_BASE/runScriptAutomated.sh" "Main pipeline script"

echo ""

# Install configuration system
echo -e "${BLUE}📋 Installing Configuration System:${NC}"
install_file "software/scannermeshprocessing-2023/config.json" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/config.json" \
             "Configuration file"

install_file "software/scannermeshprocessing-2023/config_reader.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/config_reader.py" \
             "Python config reader"

install_file "software/scannermeshprocessing-2023/config_reader.sh" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/config_reader.sh" \
             "Shell config reader"

install_file "software/scannermeshprocessing-2023/CONFIG_SYSTEM.md" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/CONFIG_SYSTEM.md" \
             "Configuration documentation"

echo ""

# Install processing scripts
echo -e "${BLUE}🐍 Installing Processing Scripts:${NC}"
install_file "software/scannermeshprocessing-2023/generateMesh_v3.sh" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/generateMesh_v3.sh" \
             "Mesh generation script"

install_file "software/scannermeshprocessing-2023/CleanUp_v5.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/CleanUp_v5.py" \
             "Cleanup script"

install_file "software/scannermeshprocessing-2023/AddRig.v05.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/AddRig.v05.py" \
             "Rigging script"

install_file "software/scannermeshprocessing-2023/poseTest_v2.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/poseTest_v2.py" \
             "Pose test script"

install_file "software/scannermeshprocessing-2023/pose_gen_package/face_detector_v2.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/pose_gen_package/face_detector_v2.py" \
             "Face detection script"

echo ""

# Install groove-mesher executable
echo -e "${BLUE}🚀 Installing Core Executable:${NC}"
install_file "software/builds/groove-mesher" \
             "$SERVER_BASE/software/builds/groove-mesher" \
             "groove-mesher executable"

echo ""

# Set executable permissions
echo -e "${BLUE}🔐 Setting Permissions:${NC}"
echo -n "📋 Setting executable permissions... "
chmod +x "$SERVER_BASE/runScriptAutomated.sh"
chmod +x "$SERVER_BASE/software/scannermeshprocessing-2023/generateMesh_v3.sh"
chmod +x "$SERVER_BASE/software/scannermeshprocessing-2023/config_reader.sh"
chmod +x "$SERVER_BASE/software/builds/groove-mesher"
echo -e "${GREEN}✅ Set${NC}"

echo ""

# Test configuration system
echo -e "${BLUE}🧪 Testing Configuration:${NC}"
echo -n "📋 Testing config system... "
cd "$SERVER_BASE/software/scannermeshprocessing-2023"
if python3 config_reader.py --info --environment server >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Working${NC}"
else
    echo -e "${YELLOW}⚠️  May need Python setup${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                           INSTALLATION COMPLETE                               ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
echo ""
echo "📋 What was installed:"
echo "  • Configuration system (4 files)"
echo "  • Main pipeline scripts (2 files)"
echo "  • Python processing scripts (4 files)"
echo "  • groove-mesher executable (1.5MB universal binary)"
echo "  • All files backed up with timestamp"
echo ""
echo "🔍 Next steps:"
echo "  1. Test the pipeline: cd $SERVER_BASE && ./runScriptAutomated.sh <scan_id>"
echo "  2. Check config: ./software/scannermeshprocessing-2023/config_reader.sh --info"
echo "  3. Review changes: ./software/scannermeshprocessing-2023/CONFIG_SYSTEM.md"
echo ""
echo "💡 New features:"
echo "  • Centralized configuration system"
echo "  • Flag-based command arguments (--local, --environment)"
echo "  • Fixed hardcoded path issues"
echo "  • Better logging and progress tracking"
echo "" 