SCANNER PIPELINE UPDATE - INSTALLATION INSTRUCTIONS
===================================================

This package contains updated scanner mesh processing pipeline files with
the following improvements:

✅ FIXES INCLUDED:
• Fixed hardcoded path issues that caused rigging failures
• Added centralized configuration system 
• Improved command-line argument handling with flags
• Better error handling and logging
• Fixed path coordination between groove-mesher and processing scripts
• Made virtual environment optional (uses system Python if scanner_env not found)

🔧 WHAT'S IN THIS PACKAGE:
• Configuration system (4 files)
• Main pipeline scripts (2 files) 
• Python processing scripts (4 files)
• groove-mesher executable (1.5MB universal binary)
• Automated installation script
• Python environment setup (requirements.txt + setup_scanner_env.sh)

📋 INSTALLATION STEPS:

1. Download and extract this zip file on the server
2. Open Terminal and navigate to the extracted folder
3. Run the installation script:
   
   chmod +x INSTALL.sh
   ./INSTALL.sh

4. The installer will:
   • Backup existing files automatically
   • Copy new files to the correct locations
   • Set proper permissions
   • Test the configuration system

5. (M4 and new machines only) Setup Python environment:
   
   chmod +x setup_scanner_env.sh
   ./setup_scanner_env.sh
   
   This creates the scanner_env virtual environment with required packages.
   M1/M2 machines can skip this step if they already have working environments.

🧪 TESTING:

After installation, test with:
   cd /Users/administrator/groove-test
   ./runScriptAutomated.sh <scan_id>

📋 NEW FEATURES:

The pipeline now supports these command options:

• ./runScriptAutomated.sh scan_id                    (uses server config)
• ./runScriptAutomated.sh scan_id --local            (forces local config) 
• ./runScriptAutomated.sh scan_id -e local           (same as above)
• ./runScriptAutomated.sh scan_id --environment local (long form)
• ./runScriptAutomated.sh scan_id --help             (show all options)

🔍 CONFIGURATION:

The new config system centralizes all paths in:
  /Users/administrator/groove-test/software/scannermeshprocessing-2023/config.json

You can check the configuration with:
  ./software/scannermeshprocessing-2023/config_reader.sh --info

📖 DOCUMENTATION:

Full documentation is available in:
  CONFIG_SYSTEM.md (included in this package)

⚠️  ROLLBACK:

If you need to rollback, the installer creates backups of all files with 
timestamps. Look for files ending in .backup.YYYYMMDD_HHMMSS

🆘 SUPPORT:

If you encounter issues:
1. Check the log files in takes/logs/
2. Verify Python environment has required packages (mediapipe, etc.)
3. Test individual components:
   - Configuration: ./software/scannermeshprocessing-2023/config_reader.sh --info
   - Pipeline: ./runScriptAutomated.sh --help

📦 PYTHON ENVIRONMENT ISSUES:

If you get "ModuleNotFoundError" errors:
1. Run the environment setup script:
   ./setup_scanner_env.sh

2. Check if packages are installed:
   source scanner_env/bin/activate
   pip list | grep -E "(opencv|mtcnn|mediapipe|tensorflow|colorama)"

3. Manually install missing packages:
   pip install -r requirements.txt

This update resolves the rigging path issues and provides a robust
configuration system for future maintenance. 