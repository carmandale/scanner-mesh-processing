# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the Scanner Mesh Processing Pipeline - a macOS-based 3D processing system that transforms photogrammetry source images into rigged, pose-testable 3D character models. The pipeline consists of 5 automated steps taking ~6 minutes total.

## Key Commands

### Running the Pipeline

```bash
# Full pipeline execution
./runScriptAutomated.sh <scan_id>                    # Uses server config
./runScriptAutomated.sh <scan_id> --local           # Uses local config

# Partial execution
./runScriptAutomated.sh <scan_id> --start-step=3    # Start from step 3
./runScriptAutomated.sh <scan_id> --steps=1,3,5     # Run specific steps
./runScriptAutomated.sh <scan_id> --dry-run         # Preview execution

# Interactive mode
./runScriptAutomated.sh <scan_id> --options         # Select steps interactively
```

### Development Commands

```bash
# Setup Python environment (Python 3.10-3.12)
./setup_scanner_env.sh

# Activate virtual environment
source scanner_env/bin/activate

# Check configuration
./config_reader.sh --info
./config_reader.sh --info local

# Install dependencies
pip install -r requirements.txt
```

### Linting and Type Checking

Currently no formal linting or type checking is configured. Python files contain `# ruff: noqa` comments but ruff is not installed or configured.

### Testing

No formal test framework is configured. Test the pipeline by running it with sample data.

## Architecture

### Pipeline Steps

1. **Generate Mesh** (~5m 52s): `generate_mesh.sh`
   - Runs `groove-mesher` photogrammetry tool
   - Executes `groove_mesh_check.py` for validation
   - Creates preview.usdz and processed mesh files

2. **Clean Up** (~9s): `cleanup.py`
   - Advanced mesh processing and orientation
   - Floor extraction and vertex adjustment
   - Uses leg/shoulder detection algorithms

3. **Face Detection** (~1s): `pose_gen_package/face_detector.py`
   - MTCNN-based facial landmark detection
   - MediaPipe pose estimation
   - Auto-rotation if face not found

4. **Add Rig** (~2s): `add_rig.py`
   - Adds skeletal armature using `skeleton_template.blend`
   - Positions bones based on pose landmarks
   - Applies weight painting

5. **Pose Test** (~5s): `pose_test.py`
   - Tests rigged model with predefined poses
   - Uses `pose_test_render.blend`
   - Generates validation renders

### Configuration System

The pipeline uses a centralized JSON configuration system:

```python
# Python usage
from config_reader import get_config
config = get_config('local')  # or 'server'
software_path = config.software_path
hdri_path = config.get_asset_path('hdri_environment')
```

```bash
# Shell usage
source config_reader.sh local
# Variables now available: $SOFTWARE_PATH, $TAKES_PATH, etc.
```

### Key Technologies

- **Blender 3.5.1+**: Required for 3D operations and USD support
- **Python Virtual Environment**: `scanner_env/` for isolated dependencies
- **Computer Vision**: OpenCV, MTCNN, MediaPipe, TensorFlow
- **3D Processing**: Custom Blender Python scripts
- **Orchestration**: Bash scripts with comprehensive error handling

### File Organization

- Main scripts now use standardized names without version suffixes
- Configuration in `config.json` with server/local environments
- Assets in same directory as scripts
- Logs in `takes/logs/scanner_processing_{scan_id}_{timestamp}.log`
- Archived/legacy code in `_ARCHIVE/` directories

### Important Implementation Notes

- Scripts require absolute paths, not relative paths
- Blender runs in background mode (`--background`)
- Face detection automatically retries with 180° rotation
- Pipeline creates/expects specific directory structure in `takes/{scan_id}/`
- Many scripts contain decorative headers that should be preserved
- Virtual environment must be activated for Python scripts to find dependencies

## Common Tasks

### Adding a New Processing Step

1. Create script following naming convention (e.g., `new_feature_v1.py`)
2. Add to `runScriptAutomated.sh` in appropriate position
3. Update step numbering and help text
4. Ensure script uses config reader for paths
5. Add logging similar to existing steps

### Debugging Failed Steps

1. Check main log: `takes/logs/scanner_processing_{scan_id}_{timestamp}.log`
2. For face detection: `takes/{scan_id}/face_detection_log.txt`
3. Verify input files exist in expected locations
4. Run individual script with `--help` for options
5. Check Blender version compatibility (3.5.1+ required)

### Updating Dependencies

1. Activate virtual environment first
2. Update `requirements.txt` with version constraints
3. Test with `pip install -r requirements.txt`
4. Note: TensorFlow <2.20.0 and MediaPipe <0.11.0 constraints are important