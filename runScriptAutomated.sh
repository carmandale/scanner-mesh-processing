#!/bin/bash

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_READER="$SCRIPT_DIR/software/scannermeshprocessing-2023/config_reader.sh"

# Default to server environment
ENVIRONMENT="server"
CLEANUP_OUTPUT=true  # Default to cleaning existing output

# Parse command line arguments and flags
SCAN_ID=""
SOFTWARE_PATH_OVERRIDE=""
TAKES_PATH_OVERRIDE=""

# Parse all arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment=*)
            ENVIRONMENT="${1#*=}"
            shift
            ;;
        --environment|-e)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --software=*)
            SOFTWARE_PATH_OVERRIDE="${1#*=}"
            shift
            ;;
        --software|-s)
            SOFTWARE_PATH_OVERRIDE="$2"
            shift 2
            ;;
        --takes=*)
            TAKES_PATH_OVERRIDE="${1#*=}"
            shift
            ;;
        --takes|-t)
            TAKES_PATH_OVERRIDE="$2"
            shift 2
            ;;
        --no-cleanup)
            CLEANUP_OUTPUT=false
            shift
            ;;
        --local)
            ENVIRONMENT="local"
            shift
            ;;
        --server)
            ENVIRONMENT="server"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 <scan_id> [options]"
            echo ""
            echo "Arguments:"
            echo "  scan_id                 Required scan identifier"
            echo ""
            echo "Options:"
            echo "  --environment, -e ENV   Environment (local/server, default: server)"
            echo "  --local                 Shorthand for --environment local"
            echo "  --server                Shorthand for --environment server"
            echo "  --software, -s PATH     Override software path"
            echo "  --takes, -t PATH        Override takes path"
            echo "  --no-cleanup            Keep existing output files"
            echo "  --help, -h              Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 scan123                    # Uses server config"
            echo "  $0 scan123 --local           # Uses local config"
            echo "  $0 scan123 --environment local"
            echo "  $0 scan123 -e local"
            echo "  $0 scan123 --no-cleanup --local"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
        *)
            if [ -z "$SCAN_ID" ]; then
                SCAN_ID="$1"
            else
                echo "Unexpected argument: $1" >&2
                echo "Use --help for usage information" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

# Load configuration for specified environment
if [[ -f "$CONFIG_READER" ]]; then
    source "$CONFIG_READER" "$ENVIRONMENT"
    echo "✅ Loaded configuration for environment: $ENVIRONMENT"
else
    echo "⚠️  Config reader not found, using fallback defaults"
    # Fallback to old behavior if config system not available
    DEFAULT_SOFTWARE_PATH="/Users/administrator/groove-test/software"
    DEFAULT_TAKES_PATH="/Users/administrator/groove-test/takes"
    export SOFTWARE_PATH="$DEFAULT_SOFTWARE_PATH"
    export TAKES_PATH="$DEFAULT_TAKES_PATH"
fi

# Apply any path overrides
SOFTWARE_PATH=${SOFTWARE_PATH_OVERRIDE:-$SOFTWARE_PATH}
TAKES_PATH=${TAKES_PATH_OVERRIDE:-$TAKES_PATH}

# Check if scan ID is provided
if [ -z "$SCAN_ID" ]; then
    echo "Usage: $0 <scan_id> [options]"
    echo ""
    echo "Arguments:"
    echo "  scan_id                 Required scan identifier"
    echo ""
    echo "Options:"
    echo "  --environment, -e ENV   Environment (local/server, default: server)"
    echo "  --local                 Shorthand for --environment local"
    echo "  --server                Shorthand for --environment server"
    echo "  --software, -s PATH     Override software path"
    echo "  --takes, -t PATH        Override takes path"
    echo "  --no-cleanup            Keep existing output files"
    echo "  --help, -h              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 scan123                    # Uses server config"
    echo "  $0 scan123 --local           # Uses local config"
    echo "  $0 scan123 --environment local"
    echo "  $0 scan123 -e local"
    echo "  $0 scan123 --no-cleanup --local"
    exit 1
fi

# Set up logging
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_DIR="$TAKES_PATH/logs"
LOG_FILE="$LOG_DIR/scanner_processing_${SCAN_ID}_${TIMESTAMP}.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Redirect all output to both console and log file
exec > >(tee -a "$LOG_FILE") 2>&1

# Log script start
log_message "=== SCANNER PROCESSING PIPELINE STARTED ==="
log_message "Script: $0"
log_message "Scan ID: $SCAN_ID"
log_message "Software Path: $SOFTWARE_PATH"
log_message "Takes Path: $TAKES_PATH"
log_message "Log File: $LOG_FILE"
log_message "=============================================="

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                           SCANNER PROCESSING PIPELINE                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Logging all output to: $LOG_FILE"
echo ""

# Debug logging
echo "📋 CONFIGURATION:"
echo "   • SCAN_ID: '$SCAN_ID'"
echo "   • ENVIRONMENT: '$ENVIRONMENT'"
echo "   • SOFTWARE_PATH: '$SOFTWARE_PATH'"
echo "   • TAKES_PATH: '$TAKES_PATH'"
echo "   • LOG_FILE: '$LOG_FILE'"
echo "   • CLEANUP_OUTPUT: $CLEANUP_OUTPUT"
if [ -d "scanner_env" ]; then
    echo "   • VIRTUAL_ENV: scanner_env (Python $(scanner_env/bin/python3 --version | cut -d' ' -f2))"
else
    echo "   • VIRTUAL_ENV: None (using system Python $(python3 --version | cut -d' ' -f2))"
fi
echo ""

# Pre-Step 1: Cleanup existing output if requested
if [ "$CLEANUP_OUTPUT" = true ]; then
    PHOTOGRAMMETRY_DIR="$TAKES_PATH/$SCAN_ID/photogrammetry"
    if [ -d "$PHOTOGRAMMETRY_DIR" ]; then
        log_message "Cleaning existing photogrammetry output directory"
        echo "🧹 CLEANUP: Removing existing output files to prevent conflicts..."
        echo "   📁 Cleaning directory: '$PHOTOGRAMMETRY_DIR'"
        
        # Remove specific files that cause conflicts
        rm -f "$PHOTOGRAMMETRY_DIR/preview.usdz" 2>/dev/null || true
        rm -rf "$PHOTOGRAMMETRY_DIR/final_usdz_files/" 2>/dev/null || true
        rm -f "$PHOTOGRAMMETRY_DIR/baked_mesh"* 2>/dev/null || true
        rm -f "$PHOTOGRAMMETRY_DIR/"*.blend 2>/dev/null || true
        rm -f "$PHOTOGRAMMETRY_DIR/"*.png 2>/dev/null || true
        
        echo "   ✅ Cleanup completed"
        log_message "Cleanup completed successfully"
    else
        echo "   ℹ️  No existing output directory found, proceeding with fresh generation"
        log_message "No existing output directory found"
    fi
    echo ""
fi

# Step 1: Generate Mesh
log_message "Starting Step 1: Generate Mesh"
echo "🔧 STEP 1: Generating Mesh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
"$SOFTWARE_PATH/scannermeshprocessing-2023/generateMesh_v3.sh" "$SCAN_ID" "$SOFTWARE_PATH" "$TAKES_PATH"
STEP1_EXIT=$?
echo ""
echo "✅ Step 1 completed with exit code: $STEP1_EXIT"
echo ""

if [ $STEP1_EXIT -ne 0 ]; then
    log_message "ERROR: Step 1 (Generate Mesh) failed with exit code $STEP1_EXIT"
    echo "❌ ERROR: Step 1 (Generate Mesh) failed with exit code $STEP1_EXIT"
    echo "   Pipeline cannot continue without a valid mesh."
    log_message "Pipeline terminated due to Step 1 failure"
    exit $STEP1_EXIT
fi
log_message "Step 1 completed successfully"

# Step 2: Clean Up
log_message "Starting Step 2: Clean Up"
echo "🧹 STEP 2: Running CleanUp"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: /Applications/Blender.app/Contents/MacOS/Blender -b -P \"$SOFTWARE_PATH/scannermeshprocessing-2023/CleanUp_v5.py\" -- --scan \"$SCAN_ID\" --path \"$TAKES_PATH\" --facing 0.5 --environment_map \"$SOFTWARE_PATH/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr\""
echo ""
/Applications/Blender.app/Contents/MacOS/Blender -b -P "$SOFTWARE_PATH/scannermeshprocessing-2023/CleanUp_v5.py" -- --scan "$SCAN_ID" --path "$TAKES_PATH" --facing 0.5 --environment_map "$SOFTWARE_PATH/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr"
STEP2_EXIT=$?
echo ""
echo "✅ Step 2 completed with exit code: $STEP2_EXIT"
echo ""

if [ $STEP2_EXIT -ne 0 ]; then
    log_message "ERROR: Step 2 (Clean Up) failed with exit code $STEP2_EXIT"
    echo "❌ ERROR: Step 2 (Clean Up) failed with exit code $STEP2_EXIT"
    echo "   Pipeline cannot continue without a cleaned mesh."
    log_message "Pipeline terminated due to Step 2 failure"
    exit $STEP2_EXIT
fi
log_message "Step 2 completed successfully"

# Step 3: Face Detection
log_message "Starting Step 3: Face Detection"
echo "👤 STEP 3: Running Face Detection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if required files exist before face detection
PNG_FILE="$TAKES_PATH/$SCAN_ID/photogrammetry/$SCAN_ID.png"
BLEND_FILE="$TAKES_PATH/$SCAN_ID/photogrammetry/$SCAN_ID.blend"

echo "🔍 Checking required files for face detection:"
if [ -f "$PNG_FILE" ]; then
    echo "   ✅ PNG file found: '$PNG_FILE'"
    log_message "Step 3: Required PNG file exists"
else
    echo "   ❌ PNG file missing: '$PNG_FILE'"
    log_message "Step 3: ERROR - Required PNG file missing: $PNG_FILE"
    echo "   ERROR: This file should have been generated by previous steps."
    echo "   Cannot proceed with face detection without the image file."
    exit 1
fi

if [ -f "$BLEND_FILE" ]; then
    echo "   ✅ Blend file found: '$BLEND_FILE'"
    log_message "Step 3: Required Blend file exists"
else
    echo "   ❌ Blend file missing: '$BLEND_FILE'"
    log_message "Step 3: ERROR - Required Blend file missing: $BLEND_FILE"
    echo "   ERROR: This file should have been generated by previous steps."
    echo "   Cannot proceed with face detection without the blend file."
    exit 1
fi

echo ""
# Choose Python command based on virtual environment availability
if [ -d "scanner_env" ]; then
    PYTHON_CMD="source scanner_env/bin/activate && python3"
    echo "Command: source scanner_env/bin/activate && python3 \"$SOFTWARE_PATH/scannermeshprocessing-2023/pose_gen_package/face_detector_v2.py\" -- --scan \"$SCAN_ID\" --path \"$TAKES_PATH\" --software \"$SOFTWARE_PATH/scannermeshprocessing-2023\" --rotmesh \"$SOFTWARE_PATH/scannermeshprocessing-2023/rotate_mesh.py\""
else
    PYTHON_CMD="python3"
    echo "Command: python3 \"$SOFTWARE_PATH/scannermeshprocessing-2023/pose_gen_package/face_detector_v2.py\" -- --scan \"$SCAN_ID\" --path \"$TAKES_PATH\" --software \"$SOFTWARE_PATH/scannermeshprocessing-2023\" --rotmesh \"$SOFTWARE_PATH/scannermeshprocessing-2023/rotate_mesh.py\""
fi
echo ""

# Execute the face detection command
if [ -d "scanner_env" ]; then
    source scanner_env/bin/activate && python3 "$SOFTWARE_PATH/scannermeshprocessing-2023/pose_gen_package/face_detector_v2.py" -- --scan "$SCAN_ID" --path "$TAKES_PATH" --software "$SOFTWARE_PATH/scannermeshprocessing-2023" --rotmesh "$SOFTWARE_PATH/scannermeshprocessing-2023/rotate_mesh.py"
else
    python3 "$SOFTWARE_PATH/scannermeshprocessing-2023/pose_gen_package/face_detector_v2.py" -- --scan "$SCAN_ID" --path "$TAKES_PATH" --software "$SOFTWARE_PATH/scannermeshprocessing-2023" --rotmesh "$SOFTWARE_PATH/scannermeshprocessing-2023/rotate_mesh.py"
fi
STEP3_EXIT=$?
echo ""
echo "✅ Step 3 completed with exit code: $STEP3_EXIT"
echo ""

if [ $STEP3_EXIT -ne 0 ]; then
    log_message "ERROR: Step 3 (Face Detection) failed with exit code $STEP3_EXIT"
    echo "❌ ERROR: Step 3 (Face Detection) failed with exit code $STEP3_EXIT"
    echo "   Pipeline cannot continue without face detection data."
    log_message "Pipeline terminated due to Step 3 failure"
    exit $STEP3_EXIT
fi
log_message "Step 3 completed successfully"

# Step 4: Add Rig
log_message "Starting Step 4: Add Rig"
echo "🦴 STEP 4: Adding Rig"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: /Applications/Blender.app/Contents/MacOS/Blender -b -P \"$SOFTWARE_PATH/scannermeshprocessing-2023/AddRig.v05.py\" -- --scan \"$SCAN_ID\" --path \"$TAKES_PATH\" --software \"$SOFTWARE_PATH/scannermeshprocessing-2023\""
echo ""
/Applications/Blender.app/Contents/MacOS/Blender -b -P "$SOFTWARE_PATH/scannermeshprocessing-2023/AddRig.v05.py" -- --scan "$SCAN_ID" --path "$TAKES_PATH" --software "$SOFTWARE_PATH/scannermeshprocessing-2023"
STEP4_EXIT=$?
echo ""
echo "✅ Step 4 completed with exit code: $STEP4_EXIT"
echo ""

if [ $STEP4_EXIT -ne 0 ]; then
    log_message "ERROR: Step 4 (Add Rig) failed with exit code $STEP4_EXIT"
    echo "❌ ERROR: Step 4 (Add Rig) failed with exit code $STEP4_EXIT"
    echo "   Pipeline cannot continue without a rigged character."
    log_message "Pipeline terminated due to Step 4 failure"
    exit $STEP4_EXIT
fi
log_message "Step 4 completed successfully"

# Step 5: Pose Test
log_message "Starting Step 5: Pose Test"
echo "🎭 STEP 5: Running Pose Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: /Applications/Blender.app/Contents/MacOS/Blender -b \"$SOFTWARE_PATH/scannermeshprocessing-2023/pose_test_render_v01.blend\" -P \"$SOFTWARE_PATH/scannermeshprocessing-2023/poseTest_v2.py\" -- --scan \"$SCAN_ID\" --path \"$TAKES_PATH\" --software \"$SOFTWARE_PATH/scannermeshprocessing-2023\""
echo ""
/Applications/Blender.app/Contents/MacOS/Blender -b "$SOFTWARE_PATH/scannermeshprocessing-2023/pose_test_render_v01.blend" -P "$SOFTWARE_PATH/scannermeshprocessing-2023/poseTest_v2.py" -- --scan "$SCAN_ID" --path "$TAKES_PATH" --software "$SOFTWARE_PATH/scannermeshprocessing-2023"
STEP5_EXIT=$?
echo ""
echo "✅ Step 5 completed with exit code: $STEP5_EXIT"
echo ""

if [ $STEP5_EXIT -ne 0 ]; then
    log_message "ERROR: Step 5 (Pose Test) failed with exit code $STEP5_EXIT"
    echo "❌ ERROR: Step 5 (Pose Test) failed with exit code $STEP5_EXIT"
    log_message "Pipeline terminated due to Step 5 failure"
    exit $STEP5_EXIT
fi
log_message "Step 5 completed successfully"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                  SUMMARY                                       ║"
echo "╠════════════════════════════════════════════════════════════════════════════════╣"
echo "║ 🔧 Step 1 (Generate Mesh):   $([ $STEP1_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
echo "║ 🧹 Step 2 (Clean Up):        $([ $STEP2_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
echo "║ 👤 Step 3 (Face Detection):  $([ $STEP3_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
echo "║ 🦴 Step 4 (Add Rig):         $([ $STEP4_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
echo "║ 🎭 Step 5 (Pose Test):       $([ $STEP5_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 All steps completed successfully!"
echo "📝 Complete log saved to: $LOG_FILE"
echo ""

log_message "=== SCANNER PROCESSING PIPELINE COMPLETED SUCCESSFULLY ==="
log_message "All steps completed with exit code 0"
log_message "Pipeline finished at $(date)"
log_message "=========================================================="