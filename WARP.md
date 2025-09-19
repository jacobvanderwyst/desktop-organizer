# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Desktop Organizer is a Python script that automatically organizes files and folders on the desktop by categorizing them into purpose-based folders. It uses intelligent classification based on file extensions, keywords, and content analysis.

## Core Architecture

### Main Components
- **DesktopOrganizer class**: Main orchestrator that handles the entire organization workflow
- **Classification system**: Multi-layered approach using extensions, keywords, MIME types, and folder content analysis
- **Configuration system**: JSON-based configuration for categories, extensions, and keywords
- **Backup system**: Creates timestamped backups before making changes
- **Logging system**: Comprehensive logging with configurable levels

### Classification Logic Flow
1. **File Extension Matching**: Primary classification method
2. **Keyword Matching**: Filename analysis with scoring system for multiple matches
3. **Shortcut Analysis**: Special handling for .lnk files including target analysis
4. **Folder Content Analysis**: Recursive analysis of folder contents (>60% threshold for classification)
5. **MIME Type Fallback**: System-based MIME type detection
6. **Default Categories**: "Other" for files, "Folders" for directories

### Configuration Categories
The project uses a sophisticated categorization system optimized for desktop organization:
- **Computer System**: Windows system tools and utilities
- **Gaming Tools**: Gaming peripherals, overlays, and streaming tools
- **Games**: Actual game executables and launchers
- **Coding Tools**: Development environments and programming tools
- **Hacking Tools**: Security and penetration testing tools
- **Media Tools**: Media players, browsers, and productivity apps

## Development Commands

### Basic Usage
```bash
# Preview organization (dry run - default behavior)
python desktop_organizer.py

# List items and their classifications only
python desktop_organizer.py --list-only

# Actually organize with confirmation
python desktop_organizer.py --no-confirm

# Quick organize without backup (use with caution)
python desktop_organizer.py --no-confirm --no-backup

# Use custom configuration
python desktop_organizer.py --config my_config.json
```

### Testing and Development
```bash
# Run with debug logging to see classification details
python desktop_organizer.py --list-only

# Test configuration changes safely
python desktop_organizer.py --dry-run

# Check classification logic for specific files
python desktop_organizer.py --list-only | grep "filename"
```

## Key Configuration

### config.json Structure
- `categories`: Defines classification rules with extensions and keywords
- `ignore_files`: Files to skip during organization
- `dry_run`: Safety mode (enabled by default)
- `create_backup`: Backup creation toggle
- `ask_confirmation`: Interactive confirmation toggle
- `log_level`: Logging verbosity (DEBUG for development)

### Adding New Categories
When adding new categories, consider:
- **Extensions**: File types that belong to this category
- **Keywords**: Terms in filenames that indicate this category
- Both are case-insensitive and support partial matching

## Important Implementation Details

### Windows Shortcut Handling
- Special `.lnk` file processing with target path analysis
- Attempts to use `win32com.client` if available, falls back to binary parsing
- Combines shortcut name and target for better classification

### Conflict Resolution
- Automatic filename numbering for conflicts (`filename_1.ext`)
- Preserves file extensions and handles files without extensions

### Backup System
- Creates timestamped backups in `backups/` directory
- Uses `shutil.copytree` for folders, `shutil.copy2` for files
- Maintains file metadata and permissions

### Error Handling
- Graceful handling of permission errors
- Comprehensive logging of all operations and errors
- Safe operation with multiple validation layers

## File Dependencies

- **Python Standard Library Only**: No external dependencies required
- **Optional**: `win32com.client` for enhanced Windows shortcut support
- **Python 3.6+** minimum requirement

## Project Structure

```
desktop-organizer/
├── desktop_organizer.py    # Main script with all functionality
├── config.json            # Configuration file with categories
├── README.md              # Comprehensive user documentation
├── .gitignore            # Standard Python/IDE exclusions
├── backups/              # Auto-created backup directory
└── desktop_organizer.log # Auto-created log file
```

## Development Notes

- All functionality is contained in a single Python file for simplicity
- Uses object-oriented design with clear separation of concerns
- Extensive logging for debugging and monitoring
- Cross-platform path handling using `pathlib.Path`
- Safe defaults with dry-run mode and confirmation prompts