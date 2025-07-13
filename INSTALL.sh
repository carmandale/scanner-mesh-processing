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

# Check if we're in the right directory (development directory)
if [ ! -f "runScriptAutomated.sh" ] || [ ! -f "config.json" ] || [ ! -f "generate_mesh.sh" ]; then
    echo -e "${RED}❌ Error: Installation files not found${NC}"
    echo "Please make sure you're running this script from the scanner mesh processing directory"
    echo "Expected files:"
    echo "  - runScriptAutomated.sh"
    echo "  - config.json"
    echo "  - generate_mesh.sh"
    echo "  - config_path_updater.py"
    echo "  - setup_scanner_env.sh"
    echo "  - And other pipeline files..."
    exit 1
fi

# Detect server base directory using current user
CURRENT_USER=$(whoami)
echo -e "${BLUE}👤 Current user: $CURRENT_USER${NC}"

# Try different possible locations
POSSIBLE_LOCATIONS=(
    "$HOME/groove-test"
    "/Users/$CURRENT_USER/groove-test"
    "/Users/administrator/groove-test"  # fallback for legacy setups
)

SERVER_BASE=""
for location in "${POSSIBLE_LOCATIONS[@]}"; do
    if [ -d "$location" ]; then
        SERVER_BASE="$location"
        echo -e "${GREEN}✅ Found groove-test at: $SERVER_BASE${NC}"
        break
    fi
done

# If not found, ask user
if [ -z "$SERVER_BASE" ]; then
    echo -e "${YELLOW}⚠️  groove-test directory not found in standard locations:${NC}"
    for location in "${POSSIBLE_LOCATIONS[@]}"; do
        echo "   - $location"
    done
    echo ""
    echo "Options:"
    echo "  1) Create new groove-test directory at $HOME/groove-test"
    echo "  2) Enter custom path"
    echo ""
    read -p "Choose option (1-2): " choice
    
    case $choice in
        1)
            SERVER_BASE="$HOME/groove-test"
            echo -e "${BLUE}📁 Creating directory structure at: $SERVER_BASE${NC}"
            ;;
        2)
            echo -n "Enter the full path to your groove-test directory: "
            read SERVER_BASE
            ;;
        *)
            echo -e "${RED}❌ Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
    
    # Create directory if it doesn't exist
    if [ ! -d "$SERVER_BASE" ]; then
        echo -e "${BLUE}📁 Creating groove-test directory: $SERVER_BASE${NC}"
        if mkdir -p "$SERVER_BASE"; then
            echo -e "${GREEN}✅ Directory created successfully${NC}"
            
            # Create basic directory structure
            mkdir -p "$SERVER_BASE/software"
            mkdir -p "$SERVER_BASE/takes"
            echo -e "${GREEN}✅ Basic directory structure created${NC}"
        else
            echo -e "${RED}❌ Failed to create directory: $SERVER_BASE${NC}"
            echo "Please check permissions and try again"
            exit 1
        fi
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

# Install main pipeline scripts
echo -e "${BLUE}🔧 Installing Main Pipeline:${NC}"
install_file "runScriptAutomated.sh" "$SERVER_BASE/runScriptAutomated.sh" "Main pipeline script"
install_file "setup_scanner_env.sh" "$SERVER_BASE/setup_scanner_env.sh" "Environment setup script"

echo ""

# Install configuration system
echo -e "${BLUE}📋 Installing Configuration System:${NC}"
install_file "config.json" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/config.json" \
             "Configuration file"

install_file "config_reader.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/config_reader.py" \
             "Python config reader"

install_file "config_reader.sh" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/config_reader.sh" \
             "Shell config reader"

install_file "CONFIG_SYSTEM.md" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/CONFIG_SYSTEM.md" \
             "Configuration documentation"

echo ""

# Update configuration paths to use detected SERVER_BASE
echo -e "${BLUE}⚙️  Updating Configuration Paths:${NC}"
CONFIG_FILE="$SERVER_BASE/software/scannermeshprocessing-2023/config.json"
UPDATER_SCRIPT="./config_path_updater.py"

if [ -f "$CONFIG_FILE" ] && [ -f "$UPDATER_SCRIPT" ]; then
    chmod +x "$UPDATER_SCRIPT"
    
    if python3 "$UPDATER_SCRIPT" "$CONFIG_FILE" "$SERVER_BASE"; then
        echo -e "${GREEN}✅ Configuration paths updated successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not update configuration automatically${NC}"
        echo -e "${YELLOW}   Please manually update paths in: $CONFIG_FILE${NC}"
    fi
else
    echo -e "${RED}❌ Config file or updater script not found${NC}"
fi

echo ""

# Install processing scripts
echo -e "${BLUE}🐍 Installing Processing Scripts:${NC}"
install_file "generate_mesh.sh" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/generate_mesh.sh" \
             "Mesh generation script"

install_file "cleanup.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/cleanup.py" \
             "Cleanup script"

install_file "add_rig.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/add_rig.py" \
             "Rigging script"

install_file "pose_test.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/pose_test.py" \
             "Pose test script"

install_file "pose_gen_package/face_detector.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/pose_gen_package/face_detector.py" \
             "Face detection script"

install_file "pose_gen_package/shape_predictor_68_face_landmarks.dat" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/pose_gen_package/shape_predictor_68_face_landmarks.dat" \
             "Face landmarks model"

install_file "pose_gen_package/pose_generator.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/pose_gen_package/pose_generator.py" \
             "Pose generator script"

# Install additional supporting files
install_file "rotate_mesh.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/rotate_mesh.py" \
             "Mesh rotation script"

install_file "kloofendal_48d_partly_cloudy_4k.hdr" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr" \
             "Environment map"

# Install blend files
install_file "pose_test_render.blend" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/pose_test_render.blend" \
             "Pose test render scene"

install_file "skeleton_template.blend" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/skeleton_template.blend" \
             "Skeleton template"

install_file "pose_test_rig.blend" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/pose_test_rig.blend" \
             "Pose test rig"

# Install mesh processing scripts
install_file "groove_mesh_check.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/groove_mesh_check.py" \
             "Mesh check script"

install_file "prep_usdz.py" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/prep_usdz.py" \
             "USDZ preparation script"

echo ""

# Install groove-mesher executable
echo -e "${BLUE}🚀 Installing Core Executable:${NC}"
install_file "builds/groove-mesher" \
             "$SERVER_BASE/software/scannermeshprocessing-2023/builds/groove-mesher" \
             "groove-mesher executable"

echo ""
install_file "requirements.txt" \
             "$SERVER_BASE/requirements.txt" \
             "Project requirements file"
install_file "install-xcode.sh" \
             "$SERVER_BASE/install-xcode.sh" \
             "Xcode installation script"
echo ""

# Set executable permissions
echo -e "${BLUE}🔐 Setting Permissions:${NC}"
echo -n "📋 Setting executable permissions... "
chmod +x "$SERVER_BASE/runScriptAutomated.sh"
chmod +x "$SERVER_BASE/setup_scanner_env.sh"
chmod +x "$SERVER_BASE/software/scannermeshprocessing-2023/generate_mesh.sh"
chmod +x "$SERVER_BASE/software/scannermeshprocessing-2023/config_reader.sh"
chmod +x "$SERVER_BASE/software/scannermeshprocessing-2023/builds/groove-mesher"
chmod +x "$SERVER_BASE/install-xcode.sh"
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
echo "  • Python processing scripts (8 files)"
echo "  • Face detection system (3 files)"
echo "  • Supporting files (5 files)"
echo "  • groove-mesher executable (1.5MB universal binary)"
echo "  • All files backed up with timestamp"
echo ""
echo "🔍 Next steps:"
echo "  1. Set up Python environment: cd $SERVER_BASE && ./setup_scanner_env.sh"
echo "  2. Test the pipeline: cd $SERVER_BASE && ./runScriptAutomated.sh <scan_id>"
echo "  3. Check config: ./software/scannermeshprocessing-2023/config_reader.sh --info"
echo "  4. Review changes: ./software/scannermeshprocessing-2023/CONFIG_SYSTEM.md"
echo ""
echo "💡 New features:"
echo "  • Centralized configuration system"
echo "  • Flag-based command arguments (--local, --environment)"
echo "  • Fixed hardcoded path issues"
echo "  • Better logging and progress tracking"
echo "" 
# Line endings standardized to LF 