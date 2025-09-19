#!/usr/bin/env python3
"""
Desktop Organizer - A script to organize desktop items by purpose
Automatically categorizes and organizes files and folders on the desktop
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
import mimetypes
import urllib.request
import re

class DesktopOrganizer:
    """Main class for organizing desktop items by purpose"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the desktop organizer"""
        self.desktop_path = Path.home() / "Desktop"
        self.config_path = config_path or "config.json"
        self.backup_dir = Path("backups")
        self.config = self._load_config()
        self._setup_logging()
        
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        default_config = {
            "categories": {
                "Documents": {
                    "extensions": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
                    "keywords": ["document", "paper", "report", "manual"]
                },
                "Images": {
                    "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
                    "keywords": ["photo", "image", "picture", "screenshot"]
                },
                "Videos": {
                    "extensions": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
                    "keywords": ["video", "movie", "clip"]
                },
                "Audio": {
                    "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
                    "keywords": ["music", "audio", "sound"]
                },
                "Archives": {
                    "extensions": [".zip", ".rar", ".7z", ".tar", ".gz"],
                    "keywords": ["archive", "backup", "compressed"]
                },
                "Applications": {
                    "extensions": [".exe", ".msi", ".dmg", ".app"],
                    "keywords": ["installer", "setup", "application"]
                },
                "Spreadsheets": {
                    "extensions": [".xls", ".xlsx", ".csv", ".ods"],
                    "keywords": ["spreadsheet", "data", "excel"]
                },
                "Presentations": {
                    "extensions": [".ppt", ".pptx", ".odp"],
                    "keywords": ["presentation", "slides", "powerpoint"]
                },
                "Code": {
                    "extensions": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php"],
                    "keywords": ["code", "script", "program", "source"]
                }
            },
            "ignore_files": [".DS_Store", "Thumbs.db", "desktop.ini"],
            "dry_run": True,
            "create_backup": True,
            "ask_confirmation": True
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Error loading config: {e}. Using defaults.")
                
        return default_config
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('desktop_organizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def scan_desktop(self) -> List[Path]:
        """Scan desktop and return list of files and folders"""
        if not self.desktop_path.exists():
            raise FileNotFoundError(f"Desktop path not found: {self.desktop_path}")
        
        items = []
        for item in self.desktop_path.iterdir():
            if item.name in self.config["ignore_files"]:
                continue
            items.append(item)
        
        self.logger.info(f"Found {len(items)} items on desktop")
        return items
    
    def classify_item(self, item_path: Path) -> str:
        """Classify an item by its purpose/type"""
        if item_path.is_dir():
            return self._classify_folder(item_path)
        else:
            return self._classify_file(item_path)
    
    def _classify_file(self, file_path: Path) -> str:
        """Classify a file by extension and name"""
        file_extension = file_path.suffix.lower()
        file_name = file_path.stem.lower()
        
        # First check by file extension
        for category, rules in self.config["categories"].items():
            if file_extension in rules["extensions"]:
                self.logger.debug(f"Classified {file_path.name} as {category} by extension")
                return category
        
        # Then check by keywords in filename
        for category, rules in self.config["categories"].items():
            for keyword in rules["keywords"]:
                if keyword in file_name:
                    self.logger.debug(f"Classified {file_path.name} as {category} by keyword '{keyword}'")
                    return category
        
        # Try to classify by MIME type as fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            main_type = mime_type.split('/')[0]
            if main_type == 'image':
                return 'Images'
            elif main_type == 'video':
                return 'Videos'
            elif main_type == 'audio':
                return 'Audio'
            elif main_type == 'text':
                return 'Documents'
        
        # Default category for unclassified items
        self.logger.debug(f"Could not classify {file_path.name}, using 'Other'")
        return 'Other'
    
    def _classify_folder(self, folder_path: Path) -> str:
        """Classify a folder by its name and contents"""
        folder_name = folder_path.name.lower()
        
        # Check folder name against keywords
        for category, rules in self.config["categories"].items():
            for keyword in rules["keywords"]:
                if keyword in folder_name:
                    self.logger.debug(f"Classified folder {folder_path.name} as {category} by keyword '{keyword}'")
                    return category
        
        # Analyze folder contents to classify
        try:
            file_types = {}
            total_files = 0
            
            for item in folder_path.iterdir():
                if item.is_file():
                    total_files += 1
                    file_category = self._classify_file(item)
                    file_types[file_category] = file_types.get(file_category, 0) + 1
            
            if total_files > 0:
                # Find the most common file type
                most_common = max(file_types.items(), key=lambda x: x[1])
                if most_common[1] / total_files > 0.6:  # If >60% of files are of one type
                    self.logger.debug(f"Classified folder {folder_path.name} as {most_common[0]} by content analysis")
                    return most_common[0]
        
        except (PermissionError, OSError) as e:
            self.logger.warning(f"Could not analyze folder contents for {folder_path.name}: {e}")
        
        # Default category for folders
        self.logger.debug(f"Could not classify folder {folder_path.name}, using 'Folders'")
        return 'Folders'
    
    def create_backup(self) -> Path:
        """Create a backup of the current desktop state"""
        if not self.config["create_backup"]:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"desktop_backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        items = self.scan_desktop()
        for item in items:
            try:
                if item.is_dir():
                    shutil.copytree(item, backup_path / item.name)
                else:
                    shutil.copy2(item, backup_path / item.name)
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Could not backup {item.name}: {e}")
        
        self.logger.info(f"Backup created at: {backup_path}")
        return backup_path
    
    def create_category_folders(self, categories: Set[str]):
        """Create folders for each category on the desktop"""
        for category in categories:
            category_path = self.desktop_path / category
            if not category_path.exists():
                try:
                    category_path.mkdir()
                    self.logger.info(f"Created folder: {category}")
                except OSError as e:
                    self.logger.error(f"Could not create folder {category}: {e}")
    
    def move_item(self, item_path: Path, category: str) -> bool:
        """Move an item to its category folder"""
        destination_folder = self.desktop_path / category
        destination_path = destination_folder / item_path.name
        
        # Handle name conflicts
        if destination_path.exists():
            base_name = item_path.stem
            extension = item_path.suffix
            counter = 1
            
            while destination_path.exists():
                if extension:
                    new_name = f"{base_name}_{counter}{extension}"
                else:
                    new_name = f"{base_name}_{counter}"
                destination_path = destination_folder / new_name
                counter += 1
        
        try:
            if self.config["dry_run"]:
                self.logger.info(f"[DRY RUN] Would move: {item_path.name} -> {category}/{destination_path.name}")
                return True
            else:
                shutil.move(str(item_path), str(destination_path))
                self.logger.info(f"Moved: {item_path.name} -> {category}/{destination_path.name}")
                return True
        except (PermissionError, OSError) as e:
            self.logger.error(f"Could not move {item_path.name}: {e}")
            return False
    
    def organize_desktop(self):
        """Main method to organize the desktop"""
        self.logger.info("Starting desktop organization")
        
        # Scan desktop items
        items = self.scan_desktop()
        if not items:
            self.logger.info("No items found to organize")
            return
        
        # Classify all items
        classifications = {}
        categories_needed = set()
        
        for item in items:
            category = self.classify_item(item)
            classifications[item] = category
            categories_needed.add(category)
        
        # Show classification results
        print("\nClassification Results:")
        print("=" * 50)
        for item, category in classifications.items():
            item_type = "📁" if item.is_dir() else "📄"
            print(f"{item_type} {item.name} -> {category}")
        
        # Ask for confirmation if needed
        if self.config["ask_confirmation"]:
            print(f"\nThis will organize {len(items)} items into {len(categories_needed)} categories.")
            if self.config["dry_run"]:
                print("This is a DRY RUN - no actual changes will be made.")
            
            response = input("\nProceed with organization? (y/N): ").lower().strip()
            if response != 'y' and response != 'yes':
                print("Organization cancelled.")
                return
        
        # Create backup if enabled
        backup_path = self.create_backup()
        if backup_path:
            print(f"Backup created: {backup_path}")
        
        # Create category folders
        self.create_category_folders(categories_needed)
        
        # Move items to their categories
        success_count = 0
        for item, category in classifications.items():
            if self.move_item(item, category):
                success_count += 1
        
        # Summary
        action = "Would organize" if self.config["dry_run"] else "Organized"
        print(f"\n{action} {success_count}/{len(items)} items successfully!")
        
        if not self.config["dry_run"]:
            self.logger.info(f"Desktop organization completed. {success_count}/{len(items)} items processed.")
        else:
            self.logger.info("Dry run completed. No changes made to desktop.")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize desktop items by purpose")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--list-only", action="store_true", help="Only list items without organizing")
    
    args = parser.parse_args()
    
    print("Desktop Organizer")
    print("================")
    
    try:
        organizer = DesktopOrganizer(args.config)
        
        # Override config with command line arguments
        if args.dry_run:
            organizer.config["dry_run"] = True
        if args.no_backup:
            organizer.config["create_backup"] = False
        if args.no_confirm:
            organizer.config["ask_confirmation"] = False
        
        if args.list_only:
            items = organizer.scan_desktop()
            print(f"\nFound {len(items)} items on desktop:")
            for item in items:
                category = organizer.classify_item(item)
                item_type = "📁" if item.is_dir() else "📄"
                print(f"  {item_type} {item.name} -> {category}")
        else:
            organizer.organize_desktop()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        logging.error(f"Error organizing desktop: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())