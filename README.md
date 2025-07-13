# Scanner Mesh Processing Pipeline

A sophisticated 5-step pipeline that transforms photogrammetry source images into rigged, pose-testable 3D character models.

## 🎯 Overview

The Scanner Mesh Processing Pipeline automatically processes raw scanner images through photogrammetry mesh generation, cleanup, face detection, rigging, and pose testing - producing production-ready 3D character assets.

**Processing Time:** ~6 minutes total
- **Step 1 (Mesh Generation):** ~5m 52s (photogrammetry)
- **Steps 2-5 (Post-processing):** ~17s (cleanup, rigging, testing)

## 🚀 Quick Start

### Prerequisites
- **macOS** (primary platform)
- **Blender 3.5.1+** installed at `/Applications/Blender.app/`
- **Python 3.10-3.12** (automatically managed via virtual environment)

### Basic Usage
```bash
# Process a complete scan
./runScriptAutomated.sh your_scan_id

# Use local configuration
./runScriptAutomated.sh your_scan_id --local

# Interactive step selection
./runScriptAutomated.sh your_scan_id --options
```

### Advanced Usage
```bash
# Run specific steps
./runScriptAutomated.sh scan_id --start-step 2 --end-step 4

# Run only certain steps
./runScriptAutomated.sh scan_id --steps "1,3,5"

# Dry run (preview execution plan)
./runScriptAutomated.sh scan_id --dry-run
```

## 📋 Installation

### Automated Setup
```bash
# 1. Clone/download the repository
# 2. Run the installer
chmod +x INSTALL.sh
./INSTALL.sh

# 3. Setup Python environment (for M4/new machines)
chmod +x setup_scanner_env.sh
./setup_scanner_env.sh
```

### Manual Verification
```bash
# Test configuration
./software/scannermeshprocessing-2023/config_reader.sh --info

# Verify pipeline
./runScriptAutomated.sh --help
```

## 🔄 Processing Pipeline

### Step 1: Mesh Generation
**Duration:** ~6 minutes | **Script:** `generate_mesh.sh`
- **Phase 1:** `groove-mesher` creates preview.usdz from source images
- **Phase 2:** `groove_mesh_check.py` processes and validates mesh
- **Input:** Raw images in `takes/{scan_id}/source/`
- **Output:** `preview.usdz`, processed mesh files

### Step 2: Mesh Cleanup
**Duration:** ~9 seconds | **Script:** `cleanup.py`
- Advanced mesh processing and orientation detection
- Floor extraction and vertex movement
- Mesh orientation using leg/shoulder detection algorithms
- Normal recalculation and hole filling

### Step 3: Face Detection & Pose Generation  
**Duration:** ~1 second | **Script:** `face_detector.py`
- MTCNN-based facial landmark detection
- Automatic mesh rotation retry if face not found
- MediaPipe pose estimation
- **Output:** `{scan_id}_results.txt` with landmark coordinates

### Step 4: Rigging
**Duration:** ~2 seconds | **Script:** `add_rig.py`
- Skeletal armature addition using `skeleton_template.blend`
- Automatic bone positioning based on pose landmarks
- Weight painting and mesh binding

### Step 5: Pose Testing
**Duration:** ~5 seconds | **Script:** `pose_test.py`
- Rigged character testing with predefined poses
- Constraint application and baking
- Validation renders

## 📁 Project Structure

```
scannermeshprocessing-2023/
├── runScriptAutomated.sh           # Main pipeline orchestrator
├── config.json                     # Environment configuration
├── config_reader.sh               # Configuration parser
│
├── generate_mesh.sh                # Step 1: Mesh generation
├── cleanup.py                      # Step 2: Mesh cleanup
├── add_rig.py                      # Step 4: Rigging
├── pose_test.py                    # Step 5: Pose testing
│
├── pose_gen_package/               # Face detection & pose generation
│   ├── face_detector.py           #   Step 3: Face detection
│   └── pose_generator.test.py     #   Pose landmark extraction
│
├── builds/                         # Compiled binaries
│   └── groove-mesher              #   Photogrammetry processor
│
├── requirements.txt                # Python dependencies
├── setup_scanner_env.sh           # Virtual environment setup
└── scanner_env/                   # Python virtual environment
```

## ⚙️ Configuration

### Environment Configuration
The system supports multiple environments via `config.json`:

```json
{
  "environments": {
    "server": {
      "software_path": "/Users/administrator/groove-test/software",
      "takes_path": "/Users/administrator/groove-test/takes"
    },
    "local": {
      "software_path": "/Users/user/scanner/software", 
      "takes_path": "/Users/user/scanner/takes"
    }
  }
}
```

### Command Line Options
```bash
# Environment selection
./runScriptAutomated.sh scan_id --environment local
./runScriptAutomated.sh scan_id --local              # shorthand

# Step control
./runScriptAutomated.sh scan_id --start-step 2       # start from step 2
./runScriptAutomated.sh scan_id --end-step 4         # end at step 4
./runScriptAutomated.sh scan_id --steps "1,3,5"      # run specific steps
./runScriptAutomated.sh scan_id --options            # interactive menu

# Utility options
./runScriptAutomated.sh scan_id --dry-run            # preview execution
./runScriptAutomated.sh scan_id --no-cleanup         # preserve existing files
./runScriptAutomated.sh scan_id --help               # show all options
```

## 🔧 Dependencies

### System Requirements
- **Blender 3.5.1+** - 3D processing and rendering
- **groove-mesher** - Photogrammetry mesh generation (included)
- **Python 3.10-3.12** - Script execution

### Python Packages (auto-installed in scanner_env)
```
opencv-python>=4.5.0          # Computer vision
mtcnn>=0.1.1                   # Face detection  
mediapipe>=0.10.0,<0.11.0      # Pose estimation
tensorflow>=2.8.0,<2.20.0     # Machine learning backend
numpy>=1.21.0,<2.0.0           # Numerical computing
colorama>=0.4.4                # Terminal colors
```

### Asset Files
- `kloofendal_48d_partly_cloudy_4k.hdr` - HDR environment map
- `skeleton_template.blend` - Rigging template
- `pose_test_render.blend` - Pose testing scenes

## 📊 Input/Output

### Input Requirements
```
takes/{scan_id}/source/          # Raw scanner images
├── IMG_001.jpg                  # Source images
├── IMG_002.jpg                  # (any format supported by groove-mesher)
└── ...
```

### Output Structure  
```
takes/{scan_id}/photogrammetry/  # Processing workspace
├── preview.usdz                 # Initial mesh (Step 1)
├── baked_mesh.usda             # Processed mesh (Step 1)
├── baked_mesh_tex0.png         # Texture map (Step 1)
├── {scan_id}.blend             # Cleaned mesh (Step 2)
├── {scan_id}.png               # Render for face detection (Step 2)
├── {scan_id}_results.txt       # Pose landmarks (Step 3)
├── {scan_id}-rig.blend         # Rigged character (Step 4)
└── pose_test_renders/          # Test renders (Step 5)
```

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError" (Python packages)**
```bash
# Setup virtual environment
./setup_scanner_env.sh

# Verify packages
source scanner_env/bin/activate  
pip list | grep -E "(opencv|mtcnn|mediapipe)"
```

**Face Detection Failing**
- Pipeline automatically retries with 180° rotation
- Check that `{scan_id}.png` exists and shows clear face
- Logs saved to `takes/{scan_id}/face_detection_log.txt`

**Blender Script Errors**
```bash
# Check Blender version
/Applications/Blender.app/Contents/MacOS/Blender --version

# Verify USD import capability
# (Blender 3.5.1+ required for USD support)
```

### Log Files
- **Pipeline logs:** `takes/logs/scanner_processing_{scan_id}_{timestamp}.log`
- **Face detection:** `takes/{scan_id}/face_detection_log.txt`
- **Individual step logs:** Embedded in pipeline log with timestamps

### Validation Commands
```bash
# Test configuration
./software/scannermeshprocessing-2023/config_reader.sh --info

# Test individual components  
./generate_mesh.sh test_scan /path/to/software /path/to/takes
python3 pose_gen_package/face_detector.py --help
```

## 📈 Performance

### Typical Processing Times
| Step | Duration | Bottleneck |
|------|----------|------------|
| Mesh Generation | 5m 52s | Photogrammetry computation |
| Cleanup | 9s | Mesh processing |
| Face Detection | 1s | Image analysis |
| Rigging | 2s | Bone positioning |
| Pose Testing | 5s | Render generation |

### System Resources
- **CPU:** High usage during mesh generation
- **Memory:** 8GB+ recommended for large meshes
- **Storage:** ~100MB per scan (temporary files cleaned)
- **GPU:** Minimal usage (CPU-based processing)

## 🔐 Security & Maintenance

### File Permissions
- Scripts require read/write access to takes directory
- Blender scripts execute with full system access
- Scan IDs are used directly in file paths (validate input)

### Regular Maintenance
- Monitor Python package compatibility
- Update Blender version compatibility  
- Validate configuration paths
- Review and rotate log files
- Check disk space for takes directory

## 🏗️ Architecture

### Components
- **Orchestrator:** `runScriptAutomated.sh` - Main pipeline controller
- **Configuration:** JSON-based environment management
- **Processing:** 5-step pipeline with Blender/Python integration
- **Monitoring:** Comprehensive logging and error handling
- **Assets:** Template files and environment maps

### Design Principles
- **Modular:** Each step is independently executable
- **Configurable:** Environment-based path management
- **Robust:** Automatic error detection and recovery
- **Extensible:** Plugin-based architecture for new steps

## 🚨 Support

### Getting Help
1. **Check logs:** `takes/logs/` for pipeline issues
2. **Verify setup:** `./config_reader.sh --info`
3. **Test components:** Individual script `--help` options
4. **Documentation:** See `CONFIG_SYSTEM.md` for advanced configuration

### Issue Reporting
Include the following information:
- Scan ID and timestamp
- Complete log files from `takes/logs/`
- System information (macOS version, Blender version)
- Configuration output from `./config_reader.sh --info`

---

**Scanner Mesh Processing Pipeline v2025** - Transforming photogrammetry into production-ready 3D assets.
