# Desktop Organizer

A Python script that automatically organizes files and folders on your desktop by their purpose and type. This tool helps maintain a clean desktop by categorizing items into appropriate folders based on file extensions, keywords, and content analysis.

## Features

- **Automatic Classification**: Intelligently categorizes files based on extensions, filenames, and MIME types
- **Folder Content Analysis**: Analyzes folder contents to determine appropriate categories
- **Safe Operation**: Creates backups before making changes and supports dry-run mode
- **Customizable Categories**: Fully configurable via JSON configuration file
- **Multiple File Types**: Supports documents, images, videos, audio, code, archives, and more
- **Conflict Resolution**: Handles naming conflicts by appending numbers
- **Comprehensive Logging**: Detailed logging of all operations
- **Interactive Confirmation**: Optional confirmation prompts before making changes

## Installation

1. Clone this repository or download the files
2. Ensure you have Python 3.6+ installed
3. No additional dependencies required (uses only standard library)

## Quick Start

### Basic Usage

```bash
# Dry run (recommended first time) - shows what would be done
python desktop_organizer.py

# Actually organize the desktop (after reviewing dry run)
python desktop_organizer.py --no-confirm
```

### Command Line Options

```bash
python desktop_organizer.py [OPTIONS]

Options:
  -c, --config PATH     Path to custom configuration file
  --dry-run            Show what would be done without making changes
  --no-backup          Skip creating backup before organizing
  --no-confirm         Skip confirmation prompt
  --list-only          Only list items and their classifications
  -h, --help           Show help message
```

### Examples

```bash
# Preview what would be organized
python desktop_organizer.py --list-only

# Organize with custom config
python desktop_organizer.py --config my_config.json

# Quick organize without prompts or backup (use with caution)
python desktop_organizer.py --no-confirm --no-backup
```

## Default Categories

The script organizes files into the following categories:

- **Documents**: PDF, Word, text files, etc.
- **Images**: Photos, screenshots, graphics
- **Videos**: Movie files, clips, recordings
- **Audio**: Music, podcasts, sound files
- **Code**: Source code files, scripts
- **Archives**: ZIP, RAR, compressed files
- **Applications**: Installers, executables
- **Spreadsheets**: Excel, CSV files
- **Presentations**: PowerPoint, Keynote files
- **Design**: Photoshop, Sketch, design files
- **Ebooks**: EPUB, MOBI, digital books
- **Fonts**: Font files
- **Folders**: Existing directories (analyzed by content)
- **Other**: Unclassified items

## Configuration

### Config File Structure

The `config.json` file allows you to customize:

```json
{
  "categories": {
    "Category Name": {
      "extensions": [".ext1", ".ext2"],
      "keywords": ["keyword1", "keyword2"]
    }
  },
  "ignore_files": [".DS_Store", "Thumbs.db"],
  "dry_run": true,
  "create_backup": true,
  "ask_confirmation": true,
  "log_level": "INFO"
}
```

### Adding Custom Categories

To add a new category, edit `config.json`:

```json
{
  "categories": {
    "3D Models": {
      "extensions": [".obj", ".fbx", ".dae", ".3ds"],
      "keywords": ["model", "3d", "mesh"]
    }
  }
}
```

### Modifying Existing Categories

You can extend existing categories:

```json
{
  "categories": {
    "Documents": {
      "extensions": [".pdf", ".doc", ".docx", ".txt", ".md"],
      "keywords": ["document", "manual", "guide", "notes"]
    }
  }
}
```

## Safety Features

### Backup Creation

By default, the script creates a backup of your desktop before making changes:
- Backups are stored in the `backups/` directory
- Named with timestamp: `desktop_backup_YYYYMMDD_HHMMSS`
- Can be disabled with `--no-backup`

### Dry Run Mode

The script runs in dry-run mode by default:
- Shows what would be done without making actual changes
- Helps you preview the organization before committing
- Disable by setting `"dry_run": false` in config or using actual organization commands

### Confirmation Prompts

Interactive confirmation before making changes:
- Shows classification results
- Confirms number of items and categories
- Can be disabled with `--no-confirm`

## Classification Logic

The script uses a multi-step classification process:

1. **File Extension Matching**: Primary method - matches file extensions
2. **Keyword Matching**: Searches for keywords in filenames
3. **MIME Type Analysis**: Uses system MIME type detection as fallback
4. **Folder Content Analysis**: For directories, analyzes contained files
5. **Default Category**: Unclassified items go to "Other" or "Folders"

## Troubleshooting

### Common Issues

**Permission Errors**
- Ensure you have read/write access to your desktop
- Close any applications using files being organized
- Run with administrator privileges if needed

**Files Not Being Classified Correctly**
- Check the configuration file for appropriate extensions/keywords
- Add custom rules for specific file types
- Review the log file for classification details

**Desktop Path Not Found**
- The script automatically detects the desktop path
- Works with standard Windows, macOS, and Linux desktop locations
- Check logs if desktop cannot be found

### Log Files

The script creates detailed logs:
- **File**: `desktop_organizer.log`
- **Level**: Configurable (DEBUG, INFO, WARNING, ERROR)
- **Content**: All operations, classifications, and errors

### Undoing Changes

To restore from backup:
1. Navigate to the `backups/` directory
2. Find the appropriate backup folder
3. Copy contents back to desktop
4. Or move organized files back manually

## Advanced Usage

### Custom Desktop Path

If you need to organize a different directory, modify the script:

```python
# In the DesktopOrganizer.__init__ method
self.desktop_path = Path("/custom/path/to/organize")
```

### Batch Processing

For multiple directories or scheduled runs:

```bash
# Create a batch script
for dir in /path/to/dir1 /path/to/dir2; do
    cd "$dir"
    python /path/to/desktop_organizer.py --no-confirm
done
```

### Integration with File Managers

You can integrate this as a custom action in file managers like:
- Windows Explorer (via PowerShell script)
- Nautilus (custom action)
- Finder (via Automator)

## Development

### Project Structure

```
desktop-organizer/
├── desktop_organizer.py    # Main script
├── config.json            # Default configuration
├── README.md              # This file
├── backups/               # Backup directory (created automatically)
└── desktop_organizer.log  # Log file (created automatically)
```

### Contributing

This is a local project not intended for public distribution, but you can:
1. Fork for personal modifications
2. Add new categories or classification rules
3. Enhance the classification algorithms
4. Add support for additional file types

## License

This project is for personal use. Modify and distribute as needed for your own purposes.

## Changelog

### v1.0.0
- Initial release with core organization features
- Support for 12 default categories
- Backup and safety features
- Configurable classification rules
- Command-line interface
- Comprehensive logging