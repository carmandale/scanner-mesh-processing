#!/bin/bash

# Default paths (server defaults - can be overridden)
DEFAULT_SOFTWARE_PATH="/Users/administrator/groove-test/software"
DEFAULT_TAKES_PATH="/Users/administrator/groove-test/takes"

# Parse command line arguments
scan_id="$1"
software_path="${2:-$DEFAULT_SOFTWARE_PATH}"
base_path="${3:-$DEFAULT_TAKES_PATH}"
feature_sensitivity="${4:-normal}"

# Check if scan ID is provided
if [ -z "$scan_id" ]; then
    echo "Usage: $0 <scan_id> [software_path] [takes_path] [feature_sensitivity]"
    echo "  scan_id: Required scan identifier"
    echo "  software_path: Optional path to software directory (default: $DEFAULT_SOFTWARE_PATH)"
    echo "  takes_path: Optional path to takes directory (default: $DEFAULT_TAKES_PATH)"
    echo "  feature_sensitivity: Optional feature sensitivity (default: normal)"
    exit 1
fi

input_folder="$base_path/$scan_id/source/"
output_folder="$base_path/$scan_id/photogrammetry/"

# Set up logging if not already set up (for standalone execution)
if [ -z "$LOG_FILE" ]; then
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    LOG_DIR="$base_path/logs"
    LOG_FILE="$LOG_DIR/generateMesh_${scan_id}_${TIMESTAMP}.log"
    mkdir -p "$LOG_DIR"
    
    # Function to log with timestamp
    log_message() {
        echo "[$(date +'%Y-%m-%d %H:%M:%S')]" $1
    }
    
    # Redirect output to log file for standalone execution
    exec > >(tee -a "$LOG_FILE") 2>&1
    
    log_message "=== GENERATEMESG_V3 STANDALONE EXECUTION ==="
    log_message "Script: $0"
    log_message "Scan ID: $scan_id"
    log_message "Software Path: $software_path"
    log_message "Takes Path: $base_path"
    log_message "Log File: $LOG_FILE"
    log_message "============================================"
else
    # Function to log with timestamp (using existing LOG_FILE)
    log_message() {
        echo "[$(date +'%Y-%m-%d %H:%M:%S')]" $1
    }
fi

log_message "generateMesh_v3.sh: Starting mesh generation process"

echo ""
echo "🔧 MESH GENERATION PROCESS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
echo "📋 Configuration:"
echo "   • Scan ID: '$scan_id'"
echo "   • Software path: '$software_path'"
echo "   • Base path: '$base_path'"
echo "   • Source folder: '$input_folder'"
echo "   • Output folder: '$output_folder'"
echo "   • Feature sensitivity: '$feature_sensitivity'"
echo ""

# Set up tool paths using the configurable software path
blender="/Applications/Blender.app/Contents/MacOS/Blender"
grooveMesher="$software_path/scannermeshprocessing-2023/builds/groove-mesher"
grooveMeshCheck="$software_path/scannermeshprocessing-2023/groove_mesh_check.py"
prepUSDZ="$software_path/scannermeshprocessing-2023/prep_usdz.py"

echo "🔍 Tool paths:"
echo "   • Blender: '$blender'"
echo "   • grooveMesher: '$grooveMesher'"
echo "   • grooveMeshCheck: '$grooveMeshCheck'"
echo "   • prepUSDZ: '$prepUSDZ'"
echo ""

# Check if paths exist
log_message "generateMesh_v3.sh: Validating paths and prerequisites"
echo "📁 Path validation:"
if [ -d "$input_folder" ]; then
    echo "   ✅ Input folder exists: '$input_folder'"
    log_message "generateMesh_v3.sh: Input folder validation passed"
else
    echo "   ❌ Input folder missing: '$input_folder'"
    echo "   ERROR: Cannot proceed without source images"
    log_message "generateMesh_v3.sh: ERROR - Input folder missing: $input_folder"
    exit 1
fi

if [ -d "$output_folder" ]; then
    echo "   ✅ Output folder exists: '$output_folder'"
    log_message "generateMesh_v3.sh: Output folder already exists"
else
    echo "   ⚠️  Output folder missing: '$output_folder'"
    echo "   📁 Creating output folder..."
    mkdir -p "$output_folder"
    if [ $? -eq 0 ]; then
        echo "   ✅ Output folder created successfully"
        log_message "generateMesh_v3.sh: Output folder created successfully"
    else
        echo "   ❌ Failed to create output folder"
        log_message "generateMesh_v3.sh: ERROR - Failed to create output folder"
        exit 1
    fi
fi

if [ -f "$grooveMesher" ]; then
    echo "   ✅ grooveMesher exists: '$grooveMesher'"
    log_message "generateMesh_v3.sh: grooveMesher validation passed"
else
    echo "   ❌ grooveMesher missing: '$grooveMesher'"
    echo "   ERROR: Cannot proceed without grooveMesher executable"
    log_message "generateMesh_v3.sh: ERROR - grooveMesher missing: $grooveMesher"
    exit 1
fi

if [ -f "$grooveMeshCheck" ]; then
    echo "   ✅ grooveMeshCheck exists: '$grooveMeshCheck'"
    log_message "generateMesh_v3.sh: grooveMeshCheck validation passed"
else
    echo "   ❌ grooveMeshCheck missing: '$grooveMeshCheck'"
    echo "   ERROR: Cannot proceed without grooveMeshCheck script"
    log_message "generateMesh_v3.sh: ERROR - grooveMeshCheck missing: $grooveMeshCheck"
    exit 1
fi

if [ -f "$prepUSDZ" ]; then
    echo "   ✅ prepUSDZ exists: '$prepUSDZ'"
    log_message "generateMesh_v3.sh: prepUSDZ validation passed"
else
    echo "   ❌ prepUSDZ missing: '$prepUSDZ'"
    echo "   ERROR: Cannot proceed without prepUSDZ script"
    log_message "generateMesh_v3.sh: ERROR - prepUSDZ missing: $prepUSDZ"
    exit 1
fi
echo ""

# Generate the preview.usdz file
log_message "generateMesh_v3.sh: Starting Phase 1 - grooveMesher execution"
echo "🎯 PHASE 1: Generating preview mesh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: \"$grooveMesher\" \"$input_folder\" \"$output_folder\" --create-preview"
echo ""
"$grooveMesher" "$input_folder" "$output_folder" --create-preview # --create-final-model --no-bounds -d medium
MESHER_EXIT=$?
echo ""
echo "✅ grooveMesher completed with exit code: $MESHER_EXIT"
echo ""

if [ $MESHER_EXIT -ne 0 ]; then
    echo "❌ ERROR: grooveMesher failed with exit code $MESHER_EXIT"
    echo "   Cannot proceed without a valid mesh preview"
    log_message "generateMesh_v3.sh: ERROR - grooveMesher failed with exit code $MESHER_EXIT"
    exit $MESHER_EXIT
fi

# Check if preview.usdz was created
preview_file="$base_path/$scan_id/photogrammetry/preview.usdz"
if [ -f "$preview_file" ]; then
    echo "   ✅ Preview file created: '$preview_file'"
    log_message "generateMesh_v3.sh: Preview file created successfully"
else
    echo "   ❌ Preview file not found: '$preview_file'"
    echo "   ERROR: grooveMesher completed but didn't create expected output"
    log_message "generateMesh_v3.sh: ERROR - Preview file not created: $preview_file"
    exit 1
fi
echo ""

# Find the bounding box of the mesh
log_message "generateMesh_v3.sh: Starting Phase 2 - grooveMeshCheck execution"
echo "🔍 PHASE 2: Mesh analysis and processing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: \"$blender\" -b -P \"$grooveMeshCheck\" -- \"$scan_id\" \"$preview_file\" \"$prepUSDZ\" \"$grooveMesher\" \"$input_folder\" \"$output_folder\" \"$feature_sensitivity\""
echo ""
"$blender" -b -P "$grooveMeshCheck" -- "$scan_id" "$preview_file" "$prepUSDZ" "$grooveMesher" "$input_folder" "$output_folder" "$feature_sensitivity"
BLENDER_EXIT=$?
echo ""
echo "✅ grooveMeshCheck completed with exit code: $BLENDER_EXIT"
echo ""

if [ $BLENDER_EXIT -ne 0 ]; then
    echo "❌ ERROR: grooveMeshCheck failed with exit code $BLENDER_EXIT"
    echo "   Mesh analysis and processing failed"
    log_message "generateMesh_v3.sh: ERROR - grooveMeshCheck failed with exit code $BLENDER_EXIT"
    exit $BLENDER_EXIT
fi

log_message "generateMesh_v3.sh: Phase 2 completed successfully"

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                         MESH GENERATION SUMMARY                               ║"
echo "╠════════════════════════════════════════════════════════════════════════════════╣"
echo "║ 🎯 Phase 1 (grooveMesher):    $MESHER_EXIT                                               ║"
echo "║ 🔍 Phase 2 (grooveMeshCheck): $BLENDER_EXIT                                               ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Mesh generation completed successfully!"
echo ""

log_message "generateMesh_v3.sh: Mesh generation process completed successfully"
log_message "generateMesh_v3.sh: grooveMesher exit code: $MESHER_EXIT"
log_message "generateMesh_v3.sh: grooveMeshCheck exit code: $BLENDER_EXIT"

exit 0
# Line endings standardized to LF