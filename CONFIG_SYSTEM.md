# Configuration System

This directory now uses a centralized configuration system to manage paths and settings across all scripts.

## Files

- `config.json` - Main configuration file with environment-specific settings
- `config_reader.py` - Python utility to read configuration 
- `config_reader.sh` - Shell script utility to read configuration
- `CleanUp_v5_config_example.py` - Example of how to update Python scripts

## Configuration File Structure

```json
{
  "environments": {
    "server": {
      "software_path": "/Users/administrator/groove-test/software",
      "takes_path": "/Users/administrator/groove-test/takes",
      "scannermeshprocessing_path": "/Users/administrator/groove-test/software/scannermeshprocessing-2023",
      "blender_path": "/Applications/Blender.app/Contents/MacOS/Blender"
    },
    "local": {
      "software_path": "/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/scanner2025/software",
      "takes_path": "/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/scanner2025/takes",
      "scannermeshprocessing_path": "/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/scanner2025/software/scannermeshprocessing-2023",
      "blender_path": "/Applications/Blender.app/Contents/MacOS/Blender"
    }
  },
  "default_environment": "server",
  "assets": {
    "hdri_environment": "kloofendal_48d_partly_cloudy_4k.hdr",
    "pose_test_rig": "pose_test_rig_v01.blend"
  },
  "executables": {
    "groove_mesher": "scannermeshprocessing-2023/builds/groove-mesher"
  }
}
```

## Usage

### Shell Scripts

```bash
# Load configuration for current environment
source config_reader.sh

# Load configuration for specific environment
source config_reader.sh local

# Get a specific path
SOFTWARE_PATH=$(./config_reader.sh --get software_path local)

# Show environment info
./config_reader.sh --info local
```

### Python Scripts

```python
from config_reader import get_config

# Load configuration
config = get_config()  # Uses default environment
config = get_config('local')  # Uses specific environment

# Get paths
software_path = config.software_path
takes_path = config.takes_path
blender_path = config.blender_path

# Get asset paths
hdri_path = config.get_asset_path('hdri_environment')
rig_path = config.get_asset_path('pose_test_rig')

# Get executable paths
groove_mesher_path = config.get_executable_path('groove_mesher')
```

## Environment Selection

The `runScriptAutomated.sh` script defaults to **server** environment.

To force **local** environment, use the `--local` flag or `--environment local`:

```bash
./runScriptAutomated.sh scan_id               # Uses server config (default)
./runScriptAutomated.sh scan_id --local       # Forces local config  
./runScriptAutomated.sh scan_id -e local      # Forces local config (short form)
./runScriptAutomated.sh scan_id --environment local  # Forces local config (long form)
```

## Benefits

1. **Centralized Configuration**: All paths in one place
2. **Environment-Aware**: Different settings for local vs server
3. **Fallback Support**: Still works if config system unavailable
4. **Consistent Paths**: No more hardcoded paths scattered across files
5. **Easy Deployment**: Just update config.json for new environments

## Migration Guide

To update a Python script to use the config system:

1. Add config import:
   ```python
   from config_reader import get_config
   ```

2. Update argument parsing:
   ```python
   parser.add_argument('-e', '--environment', help="environment", default=None)
   parser.add_argument('-m', '--path', help="directory", default=None)
   
   args = parser.parse_args()
   config = get_config(args.environment)
   
   # Use config defaults if not specified
   if args.path is None:
       args.path = config.takes_path
   ```

3. Use config properties instead of hardcoded paths:
   ```python
   # Instead of hardcoded paths
   hdri_path = "/path/to/hdri.hdr"
   
   # Use config
   hdri_path = config.get_asset_path('hdri_environment')
   ```

## Testing

Test the configuration system:

```bash
# Test shell reader
./config_reader.sh --info local
./config_reader.sh --info server

# Test Python reader  
python3 config_reader.py --info --environment local
python3 config_reader.py --info --environment server

# Test path retrieval
./config_reader.sh --get software_path local
python3 config_reader.py --path software_path --environment local
``` 