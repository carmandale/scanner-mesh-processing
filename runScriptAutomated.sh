#!/bin/bash

set -e
# Record start time for pipeline execution
PIPELINE_START=$(date +%s)

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to find config reader in multiple locations
find_config_reader() {
    local possible_paths=(
        "$SCRIPT_DIR/config_reader.sh"                                    # Same directory as script
        "$SCRIPT_DIR/software/scannermeshprocessing-2023/config_reader.sh" # Original expected location
        "$SCRIPT_DIR/../config_reader.sh"                                 # Parent directory
        "$SCRIPT_DIR/../../config_reader.sh"                              # Grandparent directory
        "$SCRIPT_DIR/../software/scannermeshprocessing-2023/config_reader.sh" # Parent/software path
        "$SCRIPT_DIR/../../software/scannermeshprocessing-2023/config_reader.sh" # Grandparent/software path
    )
    
    for path in "${possible_paths[@]}"; do
        if [[ -f "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Try to find config reader
echo "🔍 Searching for config reader from script location: $SCRIPT_DIR"
if CONFIG_READER=$(find_config_reader); then
    echo "📍 Found config reader at: $CONFIG_READER"
else
    echo "⚠️  Config reader not found in expected locations"
    CONFIG_READER=""
fi

# Default to server environment
ENVIRONMENT="server"
CLEANUP_OUTPUT=true  # Default to cleaning existing output

# Step control variables (default: run all steps)
RUN_STEP1=true
RUN_STEP2=true
RUN_STEP3=true
RUN_STEP4=true
RUN_STEP5=true
SHOW_OPTIONS=false
DRY_RUN=false
STEP_CONTROL_USED=false

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
        --options|-o)
            SHOW_OPTIONS=true
            STEP_CONTROL_USED=true
            shift
            ;;
        --start-step=*)
            START_STEP="${1#*=}"
            STEP_CONTROL_USED=true
            shift
            ;;
        --end-step=*)
            END_STEP="${1#*=}"
            STEP_CONTROL_USED=true
            shift
            ;;
        --steps=*)
            CUSTOM_STEPS="${1#*=}"
            STEP_CONTROL_USED=true
            shift
            ;;
        --skip-step=*)
            SKIP_STEP="${1#*=}"
            STEP_CONTROL_USED=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            STEP_CONTROL_USED=true
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
            echo ""
            echo "Step Control Options:"
            echo "  --options, -o           Interactive step selection"
            echo "  --start-step=N          Start from step N (1-5)"
            echo "  --end-step=N            End at step N (1-5)"
            echo "  --steps=N,M,P           Run only specific steps"
            echo "  --skip-step=N           Skip specific step"
            echo "  --dry-run               Show execution plan without running"
            echo "  --help, -h              Show this help"
            echo ""
            echo "Pipeline Steps:"
            echo "  1. Generate Mesh        Create 3D mesh from source images"
            echo "  2. Clean Up             Process and orient the mesh"
            echo "  3. Face Detection       Detect facial landmarks and pose data"
            echo "  4. Add Rig              Add skeletal armature for animation"
            echo "  5. Pose Test            Test poses and generate final renders"
            echo ""
            echo "Examples:"
            echo "  $0 scan123                          # Run all steps (server config)"
            echo "  $0 scan123 --local                 # Run all steps (local config)"
            echo "  $0 scan123 --local -o              # Interactive step selection"
            echo "  $0 scan123 --local --start-step=3  # Start from face detection"
            echo "  $0 scan123 --local --steps=1,4,5   # Run only steps 1, 4, and 5"
            echo "  $0 scan123 --local --dry-run       # Preview execution plan"
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
    
    # Function to find scannermeshprocessing directory
    find_scannermeshprocessing_dir() {
        local possible_paths=(
            "$SCRIPT_DIR"                                                     # Script is in scannermeshprocessing dir
            "$SCRIPT_DIR/scannermeshprocessing-2023"                          # Script is in parent dir
            "$SCRIPT_DIR/software/scannermeshprocessing-2023"                 # Script is in grandparent dir
            "$SCRIPT_DIR/../scannermeshprocessing-2023"                       # Script is in subdirectory
            "$SCRIPT_DIR/../../scannermeshprocessing-2023"                    # Script is in deeper subdirectory
            "$SCRIPT_DIR/../software/scannermeshprocessing-2023"              # Script is in sibling directory
        )
        
        for path in "${possible_paths[@]}"; do
            if [[ -d "$path" ]] && [[ -f "$path/config.json" ]]; then
                echo "$path"
                return 0
            fi
        done
        
        return 1
    }
    
    # Try to find scannermeshprocessing directory and derive paths
    echo "🔍 Searching for scannermeshprocessing directory..."
    if SCANNERMESHPROCESSING_DIR=$(find_scannermeshprocessing_dir); then
        echo "📍 Found scannermeshprocessing directory at: $SCANNERMESHPROCESSING_DIR"
        
        # Derive software and takes paths from the scannermeshprocessing directory
        DETECTED_SOFTWARE_PATH="$(dirname "$SCANNERMESHPROCESSING_DIR")"
        DETECTED_TAKES_PATH="$(dirname "$DETECTED_SOFTWARE_PATH")/takes"
        
        echo "📍 Detected software path: $DETECTED_SOFTWARE_PATH"
        echo "📍 Detected takes path: $DETECTED_TAKES_PATH"
        
        export SOFTWARE_PATH="$DETECTED_SOFTWARE_PATH"
        export TAKES_PATH="$DETECTED_TAKES_PATH"
        export SCANNERMESHPROCESSING_PATH="$SCANNERMESHPROCESSING_DIR"
        export BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/Blender"
        
        echo "✅ Using detected paths for fallback configuration"
    else
        echo "❌ Could not find scannermeshprocessing directory"
        echo "   Please ensure this script is run from within or near the scannermeshprocessing-2023 directory"
        echo "   Or use --software and --takes parameters to specify paths manually"
        exit 1
    fi
fi

# Apply any path overrides
SOFTWARE_PATH=${SOFTWARE_PATH_OVERRIDE:-$SOFTWARE_PATH}
TAKES_PATH=${TAKES_PATH_OVERRIDE:-$TAKES_PATH}

# Function to apply step control flags
apply_step_flags() {
    # Apply start-step flag
    if [ -n "$START_STEP" ]; then
        case $START_STEP in
            1) ;;  # Run all steps
            2) RUN_STEP1=false ;;
            3) RUN_STEP1=false; RUN_STEP2=false ;;
            4) RUN_STEP1=false; RUN_STEP2=false; RUN_STEP3=false ;;
            5) RUN_STEP1=false; RUN_STEP2=false; RUN_STEP3=false; RUN_STEP4=false ;;
            *) echo "❌ ERROR: Invalid start step '$START_STEP'. Must be 1-5."; exit 1 ;;
        esac
    fi
    
    # Apply end-step flag
    if [ -n "$END_STEP" ]; then
        case $END_STEP in
            1) RUN_STEP2=false; RUN_STEP3=false; RUN_STEP4=false; RUN_STEP5=false ;;
            2) RUN_STEP3=false; RUN_STEP4=false; RUN_STEP5=false ;;
            3) RUN_STEP4=false; RUN_STEP5=false ;;
            4) RUN_STEP5=false ;;
            5) ;;  # Run through all steps
            *) echo "❌ ERROR: Invalid end step '$END_STEP'. Must be 1-5."; exit 1 ;;
        esac
    fi
    
    # Apply custom steps flag
    if [ -n "$CUSTOM_STEPS" ]; then
        RUN_STEP1=false; RUN_STEP2=false; RUN_STEP3=false; RUN_STEP4=false; RUN_STEP5=false
        IFS=',' read -ra STEPS <<< "$CUSTOM_STEPS"
        for step in "${STEPS[@]}"; do
            case $step in
                1) RUN_STEP1=true ;;
                2) RUN_STEP2=true ;;
                3) RUN_STEP3=true ;;
                4) RUN_STEP4=true ;;
                5) RUN_STEP5=true ;;
                *) echo "❌ ERROR: Invalid step '$step'. Must be 1-5."; exit 1 ;;
            esac
        done
    fi
    
    # Apply skip-step flag
    if [ -n "$SKIP_STEP" ]; then
        case $SKIP_STEP in
            1) RUN_STEP1=false ;;
            2) RUN_STEP2=false ;;
            3) RUN_STEP3=false ;;
            4) RUN_STEP4=false ;;
            5) RUN_STEP5=false ;;
            *) echo "❌ ERROR: Invalid skip step '$SKIP_STEP'. Must be 1-5."; exit 1 ;;
        esac
    fi
}

# Function to show interactive options menu
show_options_menu() {
    echo ""
    echo "🔧 SCANNER PROCESSING PIPELINE - STEP SELECTION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Select steps to run for scan: $SCAN_ID"
    echo ""
    echo "[1] $([ "$RUN_STEP1" = true ] && echo "✅" || echo "⏭️ ") Step 1: Generate Mesh"
    echo "[2] $([ "$RUN_STEP2" = true ] && echo "✅" || echo "⏭️ ") Step 2: Clean Up"
    echo "[3] $([ "$RUN_STEP3" = true ] && echo "✅" || echo "⏭️ ") Step 3: Face Detection"
    echo "[4] $([ "$RUN_STEP4" = true ] && echo "✅" || echo "⏭️ ") Step 4: Add Rig"
    echo "[5] $([ "$RUN_STEP5" = true ] && echo "✅" || echo "⏭️ ") Step 5: Pose Test"
    echo ""
    echo "Options:"
    echo "  a) Run all steps (default)"
    echo "  1-5) Toggle individual step"
    echo "  s) Start from step [1-5]:"
    echo "  e) End at step [1-5]:"
    echo "  r) Reset to all steps"
    echo "  d) Dry run (show plan)"
    echo "  h) Help"
    echo "  c) Continue with current selection"
    echo "  q) Quit"
    echo ""
    
    while true; do
        read -p "Enter choice [c]: " choice
        choice=${choice:-c}
        
        case $choice in
            a)
                RUN_STEP1=true; RUN_STEP2=true; RUN_STEP3=true; RUN_STEP4=true; RUN_STEP5=true
                show_options_menu
                return
                ;;
            1)
                RUN_STEP1=$([ "$RUN_STEP1" = true ] && echo false || echo true)
                show_options_menu
                return
                ;;
            2)
                RUN_STEP2=$([ "$RUN_STEP2" = true ] && echo false || echo true)
                show_options_menu
                return
                ;;
            3)
                RUN_STEP3=$([ "$RUN_STEP3" = true ] && echo false || echo true)
                show_options_menu
                return
                ;;
            4)
                RUN_STEP4=$([ "$RUN_STEP4" = true ] && echo false || echo true)
                show_options_menu
                return
                ;;
            5)
                RUN_STEP5=$([ "$RUN_STEP5" = true ] && echo false || echo true)
                show_options_menu
                return
                ;;
            s)
                read -p "Start from step [1-5]: " start_step
                if [[ "$start_step" =~ ^[1-5]$ ]]; then
                    START_STEP=$start_step
                    apply_step_flags
                    show_options_menu
                    return
                else
                    echo "❌ Invalid step. Please enter 1-5."
                fi
                ;;
            e)
                read -p "End at step [1-5]: " end_step
                if [[ "$end_step" =~ ^[1-5]$ ]]; then
                    END_STEP=$end_step
                    apply_step_flags
                    show_options_menu
                    return
                else
                    echo "❌ Invalid step. Please enter 1-5."
                fi
                ;;
            r)
                RUN_STEP1=true; RUN_STEP2=true; RUN_STEP3=true; RUN_STEP4=true; RUN_STEP5=true
                START_STEP=""; END_STEP=""
                show_options_menu
                return
                ;;
            d)
                DRY_RUN=true
                return
                ;;
            h)
                echo ""
                echo "📋 Step Descriptions:"
                echo "  Step 1: Generate Mesh      - Create 3D mesh from source images"
                echo "  Step 2: Clean Up          - Process and orient the mesh"
                echo "  Step 3: Face Detection    - Detect facial landmarks and pose data"
                echo "  Step 4: Add Rig           - Add skeletal armature for animation"
                echo "  Step 5: Pose Test         - Test poses and generate final renders"
                echo ""
                echo "💡 Tips:"
                echo "  - Each step depends on the previous step's output"
                echo "  - You can start from any step if previous outputs exist"
                echo "  - Use dry run to preview what will be executed"
                echo ""
                ;;
            c)
                return
                ;;
            q)
                echo "❌ Pipeline cancelled by user"
                exit 0
                ;;
            *)
                echo "❌ Invalid choice. Please try again."
                ;;
        esac
    done
}

# Function to validate step dependencies
validate_dependencies() {
    # Only validate dependencies if step control options were used
    if [ "$STEP_CONTROL_USED" = false ]; then
        return 0
    fi
    
    local photogrammetry_dir="$TAKES_PATH/$SCAN_ID/photogrammetry"
    local issues=false
    
    echo "🔍 Validating step dependencies..."
    
    # Check Step 2 dependencies
    if [ "$RUN_STEP2" = true ] && [ "$RUN_STEP1" = false ]; then
        if [ ! -f "$photogrammetry_dir/preview.usdz" ]; then
            echo "⚠️  Step 2 requires 'preview.usdz' from Step 1"
            issues=true
        fi
    fi
    
    # Check Step 3 dependencies
    if [ "$RUN_STEP3" = true ] && [ "$RUN_STEP2" = false ]; then
        if [ ! -f "$photogrammetry_dir/$SCAN_ID.png" ] || [ ! -f "$photogrammetry_dir/$SCAN_ID.blend" ]; then
            echo "⚠️  Step 3 requires '.png' and '.blend' files from Step 2"
            issues=true
        fi
    fi
    
    # Check Step 4 dependencies
    if [ "$RUN_STEP4" = true ] && [ "$RUN_STEP3" = false ]; then
        if [ ! -f "$photogrammetry_dir/${SCAN_ID}_results.txt" ]; then
            echo "⚠️  Step 4 requires '${SCAN_ID}_results.txt' from Step 3"
            issues=true
        fi
    fi
    
    # Check Step 5 dependencies
    if [ "$RUN_STEP5" = true ] && [ "$RUN_STEP4" = false ]; then
        if [ ! -f "$photogrammetry_dir/$SCAN_ID-rig.blend" ]; then
            echo "⚠️  Step 5 requires '$SCAN_ID-rig.blend' from Step 4"
            issues=true
        fi
    fi
    
    if [ "$issues" = true ]; then
        echo ""
        echo "❌ DEPENDENCY ISSUES DETECTED"
        echo "   Some selected steps are missing required input files."
        echo "   Either include the prerequisite steps or ensure the files exist."
        echo ""
        
        read -p "Continue anyway? [y/N]: " continue_choice
        if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
            echo "❌ Pipeline cancelled due to dependency issues"
            exit 1
        fi
    fi
}

# Function to show execution plan
show_execution_plan() {
    echo ""
    echo "📋 EXECUTION PLAN:"
    echo "   • SCAN_ID: '$SCAN_ID'"
    echo "   • ENVIRONMENT: '$ENVIRONMENT'"
    echo "   • SOFTWARE_PATH: '$SOFTWARE_PATH'"
    echo "   • TAKES_PATH: '$TAKES_PATH'"
    echo ""
    echo "   STEPS TO RUN:"
    [ "$RUN_STEP1" = true ] && echo "   ✅ Step 1: Generate Mesh" || echo "   ⏭️  Step 1: Generate Mesh (SKIPPED)"
    [ "$RUN_STEP2" = true ] && echo "   ✅ Step 2: Clean Up" || echo "   ⏭️  Step 2: Clean Up (SKIPPED)"
    [ "$RUN_STEP3" = true ] && echo "   ✅ Step 3: Face Detection" || echo "   ⏭️  Step 3: Face Detection (SKIPPED)"
    [ "$RUN_STEP4" = true ] && echo "   ✅ Step 4: Add Rig" || echo "   ⏭️  Step 4: Add Rig (SKIPPED)"
    [ "$RUN_STEP5" = true ] && echo "   ✅ Step 5: Pose Test" || echo "   ⏭️  Step 5: Pose Test (SKIPPED)"
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        echo "🧪 DRY RUN MODE - No steps will be executed"
        echo ""
        exit 0
    elif [ "$STEP_CONTROL_USED" = true ]; then
        # Only prompt for confirmation if user used step control options
        read -p "Continue with this execution plan? [Y/n]: " continue_choice
        if [[ "$continue_choice" =~ ^[Nn]$ ]]; then
            echo "❌ Pipeline cancelled by user"
            exit 0
        fi
    else
        # Legacy behavior: show plan but continue automatically
        echo "🚀 Starting pipeline execution..."
        echo ""
    fi
}

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

# Apply step control flags
apply_step_flags

# Show interactive options menu if requested
if [ "$SHOW_OPTIONS" = true ]; then
    show_options_menu
fi

# Validate dependencies and show execution plan
validate_dependencies
show_execution_plan

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
if [ "$RUN_STEP1" = true ]; then
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
else
    STEP1_EXIT=0
    log_message "Step 1 (Generate Mesh) skipped"
    echo "⏭️  STEP 1: Generate Mesh (SKIPPED)"
    echo ""
fi

# Step 2: Clean Up
if [ "$RUN_STEP2" = true ]; then
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
else
    STEP2_EXIT=0
    log_message "Step 2 (Clean Up) skipped"
    echo "⏭️  STEP 2: Clean Up (SKIPPED)"
    echo ""
fi

# Step 3: Face Detection
if [ "$RUN_STEP3" = true ]; then
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
else
    STEP3_EXIT=0
    log_message "Step 3 (Face Detection) skipped"
    echo "⏭️  STEP 3: Face Detection (SKIPPED)"
    echo ""
fi

# Step 4: Add Rig
if [ "$RUN_STEP4" = true ]; then
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
else
    STEP4_EXIT=0
    log_message "Step 4 (Add Rig) skipped"
    echo "⏭️  STEP 4: Add Rig (SKIPPED)"
    echo ""
fi

# Step 5: Pose Test
if [ "$RUN_STEP5" = true ]; then
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
else
    STEP5_EXIT=0
    log_message "Step 5 (Pose Test) skipped"
    echo "⏭️  STEP 5: Pose Test (SKIPPED)"
    echo ""
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                  SUMMARY                                       ║"
echo "╠════════════════════════════════════════════════════════════════════════════════╣"
if [ "$RUN_STEP1" = true ]; then
    echo "║ 🔧 Step 1 (Generate Mesh):   $([ $STEP1_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
else
    echo "║ 🔧 Step 1 (Generate Mesh):   ⏭️  SKIPPED                                       ║"
fi
if [ "$RUN_STEP2" = true ]; then
    echo "║ 🧹 Step 2 (Clean Up):        $([ $STEP2_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
else
    echo "║ 🧹 Step 2 (Clean Up):        ⏭️  SKIPPED                                       ║"
fi
if [ "$RUN_STEP3" = true ]; then
    echo "║ 👤 Step 3 (Face Detection):  $([ $STEP3_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
else
    echo "║ 👤 Step 3 (Face Detection):  ⏭️  SKIPPED                                       ║"
fi
if [ "$RUN_STEP4" = true ]; then
    echo "║ 🦴 Step 4 (Add Rig):         $([ $STEP4_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
else
    echo "║ 🦴 Step 4 (Add Rig):         ⏭️  SKIPPED                                       ║"
fi
if [ "$RUN_STEP5" = true ]; then
    echo "║ 🎭 Step 5 (Pose Test):       $([ $STEP5_EXIT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")                                       ║"
else
    echo "║ 🎭 Step 5 (Pose Test):       ⏭️  SKIPPED                                       ║"
fi
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Calculate overall success
TOTAL_FAILURE=0
if [ "$RUN_STEP1" = true ] && [ $STEP1_EXIT -ne 0 ]; then TOTAL_FAILURE=$((TOTAL_FAILURE + 1)); fi
if [ "$RUN_STEP2" = true ] && [ $STEP2_EXIT -ne 0 ]; then TOTAL_FAILURE=$((TOTAL_FAILURE + 1)); fi
if [ "$RUN_STEP3" = true ] && [ $STEP3_EXIT -ne 0 ]; then TOTAL_FAILURE=$((TOTAL_FAILURE + 1)); fi
if [ "$RUN_STEP4" = true ] && [ $STEP4_EXIT -ne 0 ]; then TOTAL_FAILURE=$((TOTAL_FAILURE + 1)); fi
if [ "$RUN_STEP5" = true ] && [ $STEP5_EXIT -ne 0 ]; then TOTAL_FAILURE=$((TOTAL_FAILURE + 1)); fi

if [ $TOTAL_FAILURE -eq 0 ]; then
    echo "🎉 All selected steps completed successfully!"
else
    echo "❌ $TOTAL_FAILURE step(s) failed!"
fi
echo "📝 Complete log saved to: $LOG_FILE"
echo ""

if [ $TOTAL_FAILURE -eq 0 ]; then
    log_message "=== SCANNER PROCESSING PIPELINE COMPLETED SUCCESSFULLY ==="
    log_message "All selected steps completed with exit code 0"
else
    log_message "=== SCANNER PROCESSING PIPELINE COMPLETED WITH FAILURES ==="
    log_message "$TOTAL_FAILURE step(s) failed"
fi
log_message "Pipeline finished at $(date)"
log_message "=========================================================="
# Record end time and compute elapsed duration
PIPELINE_END=$(date +%s)
ELAPSED=$((PIPELINE_END - PIPELINE_START))
if [ $ELAPSED -lt 60 ]; then
    log_message "Total execution time: ${ELAPSED} seconds"
else
    MINUTES=$((ELAPSED/60))
    SECONDS=$((ELAPSED%60))
    log_message "Total execution time: ${MINUTES} minutes ${SECONDS} seconds"
fi

# Line endings standardized to LF