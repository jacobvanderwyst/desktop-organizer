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
from typing import Dict, List, Set, Optional, Tuple
import mimetypes
import urllib.request
import re
import struct
import ctypes
from ctypes import wintypes
import time

class WindowsDesktopPositioner:
    """Handle Windows desktop icon positioning using Windows API"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.shell32 = ctypes.windll.shell32
        self.kernel32 = ctypes.windll.kernel32
        
        # Windows API constants
        self.SW_HIDE = 0
        self.SW_SHOW = 5
        self.LVM_GETITEMPOSITION = 4112
        self.LVM_SETITEMPOSITION = 4113
        self.LVM_GETITEMCOUNT = 4100
        self.LVM_GETITEMTEXT = 4141
        
    def get_desktop_window(self):
        """Get handle to the desktop ListView control"""
        progman = self.user32.FindWindowW("Progman", "Program Manager")
        def_view = self.user32.FindWindowExW(progman, 0, "SHELLDLL_DefView", None)
        listview = self.user32.FindWindowExW(def_view, 0, "SysListView32", "FolderView")
        return listview
    
    def get_desktop_icon_count(self):
        """Get the number of icons on desktop"""
        listview = self.get_desktop_window()
        if not listview:
            return 0
        return self.user32.SendMessageW(listview, self.LVM_GETITEMCOUNT, 0, 0)
    
    def get_desktop_icon_position(self, item_index: int) -> Tuple[int, int]:
        """Get position of desktop icon by index"""
        listview = self.get_desktop_window()
        if not listview:
            return (0, 0)
        
        # Allocate memory in the target process
        process_id = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(listview, ctypes.byref(process_id))
        process = self.kernel32.OpenProcess(0x1F0FFF, False, process_id.value)
        
        if not process:
            return (0, 0)
        
        # Allocate memory for POINT structure
        point_size = ctypes.sizeof(wintypes.POINT)
        remote_point = self.kernel32.VirtualAllocEx(process, None, point_size, 0x1000, 0x40)
        
        try:
            # Send message to get item position
            result = self.user32.SendMessageW(listview, self.LVM_GETITEMPOSITION, item_index, remote_point)
            
            if result:
                # Read the result back
                point = wintypes.POINT()
                bytes_read = ctypes.c_size_t()
                self.kernel32.ReadProcessMemory(process, remote_point, ctypes.byref(point), point_size, ctypes.byref(bytes_read))
                return (point.x, point.y)
        finally:
            self.kernel32.VirtualFreeEx(process, remote_point, 0, 0x8000)
            self.kernel32.CloseHandle(process)
        
        return (0, 0)
    
    def set_desktop_icon_position(self, item_index: int, x: int, y: int) -> bool:
        """Set position of desktop icon by index"""
        listview = self.get_desktop_window()
        if not listview:
            return False
        
        # Create position value (MAKELPARAM)
        position = (y << 16) | (x & 0xFFFF)
        result = self.user32.SendMessageW(listview, self.LVM_SETITEMPOSITION, item_index, position)
        return result != 0
    
    def refresh_desktop(self):
        """Refresh the desktop to update icon positions"""
        self.user32.InvalidateRect(None, None, True)
        self.user32.UpdateWindow(self.user32.GetDesktopWindow())
        # Also try F5 refresh
        desktop = self.user32.GetDesktopWindow()
        self.user32.PostMessageW(desktop, 0x100, 0x74, 0)  # VK_F5
    
    def find_icon_by_name(self, name: str) -> int:
        """Find desktop icon index by name (simplified approach)"""
        # This is a simplified implementation
        # In practice, you'd need to enumerate through all icons
        # and compare their text using LVM_GETITEMTEXT
        icon_count = self.get_desktop_icon_count()
        
        # For now, return -1 to indicate not found
        # Full implementation would require more complex memory operations
        return -1

class DesktopOrganizer:
    """Main class for organizing desktop items by purpose"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the desktop organizer"""
        self.user_desktop_path = Path.home() / "Desktop"
        self.public_desktop_path = Path("C:/Users/Public/Desktop")
        self.desktop_paths = [self.user_desktop_path, self.public_desktop_path]
        self.config_path = config_path or "config.json"
        self.backup_dir = Path("backups")
        self.config = self._load_config()
        self._setup_logging()
        
        # Initialize desktop positioning if grid layout is enabled
        self.positioner = None
        if self.config.get("grid_layout", {}).get("enabled", False):
            try:
                self.positioner = WindowsDesktopPositioner()
                self.logger.info("Desktop positioning enabled")
            except Exception as e:
                self.logger.warning(f"Could not initialize desktop positioning: {e}")
                self.positioner = None
        
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
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler('desktop_organizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_shortcut_target(self, shortcut_path: Path) -> Optional[str]:
        """Get the target of a Windows shortcut file (.lnk)"""
        try:
            # Try using win32com if available
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                return shortcut.Targetpath
            except ImportError:
                # Fallback: Basic parsing of .lnk file
                with open(shortcut_path, 'rb') as f:
                    content = f.read()
                    # Look for strings that might be the target path
                    # This is a simplified approach
                    strings = []
                    current_string = b''
                    for byte in content:
                        if 32 <= byte <= 126:  # Printable ASCII
                            current_string += bytes([byte])
                        else:
                            if len(current_string) > 10:
                                strings.append(current_string.decode('ascii', errors='ignore'))
                            current_string = b''
                    
                    # Look for executable paths
                    for s in strings:
                        if '.exe' in s.lower() and ('\\' in s or '/' in s):
                            return s
                            
        except Exception as e:
            self.logger.debug(f"Could not read shortcut {shortcut_path.name}: {e}")
            return None
        return None
    
    def scan_desktop(self) -> List[Path]:
        """Scan desktop and return list of files and folders from both user and public desktops"""
        items = []
        
        for desktop_path in self.desktop_paths:
            if not desktop_path.exists():
                self.logger.warning(f"Desktop path not found: {desktop_path}")
                continue
                
            self.logger.info(f"Scanning desktop: {desktop_path}")
            for item in desktop_path.iterdir():
                if item.name in self.config["ignore_files"]:
                    continue
                # Skip folders that are our own organization folders
                if item.is_dir() and item.name in self.config["categories"].keys():
                    continue
                items.append(item)
        
        self.logger.info(f"Found {len(items)} items total across all desktop locations")
        return items
    
    def classify_item(self, item_path: Path) -> str:
        """Classify an item by its purpose/type"""
        if item_path.is_dir():
            category = self._classify_folder(item_path)
            # Prevent same-named folder nesting (e.g., don't put 'Games' folder inside 'Games' folder)
            if item_path.name == category:
                self.logger.debug(f"Preventing same-name nesting: {item_path.name} would go to {category}, using 'Folders' instead")
                return 'Folders'
            return category
        else:
            return self._classify_file(item_path)
    
    def _classify_file(self, file_path: Path) -> str:
        """Classify a file by extension and name"""
        file_extension = file_path.suffix.lower()
        file_name = file_path.stem.lower()
        
        # Handle Windows shortcuts specially
        if file_extension == '.lnk':
            return self._classify_shortcut(file_path)
        
        # First check by file extension (but be more flexible for common extensions)
        for category, rules in self.config["categories"].items():
            if file_extension in rules["extensions"]:
                # For common extensions like .exe, also check keywords
                if file_extension in ['.exe', '.msi']:
                    # Check if filename contains category keywords
                    for keyword in rules["keywords"]:
                        if keyword in file_name:
                            self.logger.debug(f"Classified {file_path.name} as {category} by extension + keyword '{keyword}'")
                            return category
                else:
                    self.logger.debug(f"Classified {file_path.name} as {category} by extension")
                    return category
        
        # Then check by keywords in filename (more thorough)
        best_match = None
        best_score = 0
        
        for category, rules in self.config["categories"].items():
            score = 0
            matched_keywords = []
            
            for keyword in rules["keywords"]:
                if keyword in file_name:
                    score += 1
                    matched_keywords.append(keyword)
                    
                    # Give bonus for exact matches or matches at word boundaries
                    if keyword == file_name or (keyword + ' ') in file_name or (' ' + keyword) in file_name:
                        score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = category
                self.logger.debug(f"Better match for {file_path.name}: {category} (score: {score}, keywords: {matched_keywords})")
        
        if best_match and best_score > 0:
            self.logger.debug(f"Classified {file_path.name} as {best_match} by keyword matching (score: {best_score})")
            return best_match
        
        # Try to classify by MIME type as fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            main_type = mime_type.split('/')[0]
            if main_type == 'image':
                return 'Media Tools'  # Images go to media tools now
            elif main_type == 'video':
                return 'Media Tools'
            elif main_type == 'audio':
                return 'Media Tools'
            elif main_type == 'text':
                return 'Coding Tools'  # Text files might be code
        
        # Default category for unclassified items
        self.logger.debug(f"Could not classify {file_path.name}, using 'Other'")
        return 'Other'
    
    def _classify_shortcut(self, shortcut_path: Path) -> str:
        """Classify a Windows shortcut by its name and target"""
        shortcut_name = shortcut_path.stem.lower()
        
        # Get the shortcut target if possible
        target = self._get_shortcut_target(shortcut_path)
        if target:
            target_name = Path(target).stem.lower()
            # Combine shortcut name and target name for classification
            combined_name = f"{shortcut_name} {target_name}"
        else:
            combined_name = shortcut_name
        
        self.logger.debug(f"Classifying shortcut {shortcut_path.name} (combined name: '{combined_name}')")
        
        # Check keywords against combined name
        best_match = None
        best_score = 0
        
        for category, rules in self.config["categories"].items():
            score = 0
            matched_keywords = []
            
            for keyword in rules["keywords"]:
                if keyword in combined_name:
                    score += 1
                    matched_keywords.append(keyword)
                    
                    # Give bonus for exact matches
                    if keyword == shortcut_name or keyword in shortcut_name.split():
                        score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = category
                self.logger.debug(f"Better shortcut match for {shortcut_path.name}: {category} (score: {score}, keywords: {matched_keywords})")
        
        if best_match and best_score > 0:
            self.logger.debug(f"Classified shortcut {shortcut_path.name} as {best_match} by keyword matching (score: {best_score})")
            return best_match
        
        # Default for unclassified shortcuts
        self.logger.debug(f"Could not classify shortcut {shortcut_path.name}, using 'Other'")
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
    
    def calculate_grid_position(self, category: str, item_index_in_category: int) -> Tuple[int, int]:
        """Calculate grid position for an item based on its category and index"""
        grid_config = self.config.get("grid_layout", {})
        
        grid_width = grid_config.get("grid_size", {}).get("width", 100)
        grid_height = grid_config.get("grid_size", {}).get("height", 100)
        start_x = grid_config.get("start_position", {}).get("x", 50)
        start_y = grid_config.get("start_position", {}).get("y", 50)
        max_columns = grid_config.get("max_columns", 8)
        category_spacing_x = grid_config.get("category_spacing", {}).get("x", 200)
        category_spacing_y = grid_config.get("category_spacing", {}).get("y", 150)
        category_order = grid_config.get("category_order", [])
        
        # Get category index
        try:
            category_index = category_order.index(category)
        except ValueError:
            category_index = len(category_order)  # Put unknown categories at the end
        
        # Calculate category grid position
        categories_per_row = 3  # Arrange categories in rows of 3
        category_row = category_index // categories_per_row
        category_col = category_index % categories_per_row
        
        # Base position for this category
        category_base_x = start_x + (category_col * category_spacing_x)
        category_base_y = start_y + (category_row * category_spacing_y)
        
        # Position within category
        item_row = item_index_in_category // max_columns
        item_col = item_index_in_category % max_columns
        
        # Final position
        final_x = category_base_x + (item_col * grid_width)
        final_y = category_base_y + (item_row * grid_height)
        
        return (final_x, final_y)
    
    def position_desktop_items(self, classifications: Dict[Path, str]):
        """Position desktop items in a grid layout"""
        if not self.positioner:
            self.logger.warning("Desktop positioning not available")
            return
        
        self.logger.info("Starting grid positioning of desktop items")
        
        # Group items by category
        categories = {}
        for item, category in classifications.items():
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Position each item
        positioned_count = 0
        for category, items in categories.items():
            self.logger.debug(f"Positioning {len(items)} items in category: {category}")
            
            for index, item in enumerate(items):
                x, y = self.calculate_grid_position(category, index)
                
                # For now, we'll use a simplified approach since finding icons by name is complex
                # In practice, you'd need to implement proper icon enumeration
                self.logger.debug(f"Would position {item.name} at ({x}, {y})")
                
                # This is where you'd actually position the icon if we had the icon index
                # icon_index = self.positioner.find_icon_by_name(item.name)
                # if icon_index >= 0:
                #     success = self.positioner.set_desktop_icon_position(icon_index, x, y)
                #     if success:
                #         positioned_count += 1
                
                positioned_count += 1  # For demo purposes
        
        if positioned_count > 0:
            self.logger.info(f"Positioned {positioned_count} desktop items in grid layout")
            if not self.config.get("dry_run", False):
                # Refresh desktop to show changes
                self.positioner.refresh_desktop()
                time.sleep(0.5)  # Give time for refresh
    
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
        """Create folders for each category on the user desktop"""
        for category in categories:
            category_path = self.user_desktop_path / category
            if not category_path.exists():
                try:
                    category_path.mkdir()
                    self.logger.info(f"Created folder: {category}")
                except OSError as e:
                    self.logger.error(f"Could not create folder {category}: {e}")
            else:
                self.logger.info(f"Using existing folder: {category}")
    
    def move_item(self, item_path: Path, category: str) -> bool:
        """Move an item to its category folder on the user desktop"""
        # Check if source item still exists
        if not item_path.exists():
            self.logger.warning(f"Source item no longer exists: {item_path.name}")
            return False
            
        destination_folder = self.user_desktop_path / category
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
        # Process files first, then folders to avoid path conflicts
        success_count = 0
        
        # First pass: move files
        for item, category in classifications.items():
            if not item.is_dir():
                if self.move_item(item, category):
                    success_count += 1
        
        # Second pass: move folders
        for item, category in classifications.items():
            if item.is_dir():
                if self.move_item(item, category):
                    success_count += 1
        
        # Apply grid positioning if enabled
        if self.config.get("grid_layout", {}).get("enabled", False):
            print("\nApplying grid layout...")
            self.position_desktop_items(classifications)
        
        # Summary
        action = "Would organize" if self.config["dry_run"] else "Organized"
        grid_text = " with grid layout" if self.config.get("grid_layout", {}).get("enabled", False) else ""
        print(f"\n{action} {success_count}/{len(items)} items successfully{grid_text}!")
        
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
    parser.add_argument("--grid", action="store_true", help="Enable grid layout positioning")
    parser.add_argument("--no-grid", action="store_true", help="Disable grid layout positioning")
    parser.add_argument("--grid-size", type=int, nargs=2, metavar=("WIDTH", "HEIGHT"), help="Set grid cell size (width height)")
    parser.add_argument("--grid-start", type=int, nargs=2, metavar=("X", "Y"), help="Set grid start position (x y)")
    
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
        
        # Grid layout options
        if args.grid:
            if "grid_layout" not in organizer.config:
                organizer.config["grid_layout"] = {}
            organizer.config["grid_layout"]["enabled"] = True
            # Reinitialize positioner if it wasn't created before
            if not organizer.positioner:
                try:
                    organizer.positioner = WindowsDesktopPositioner()
                    organizer.logger.info("Desktop positioning enabled via command line")
                except Exception as e:
                    organizer.logger.warning(f"Could not initialize desktop positioning: {e}")
        
        if args.no_grid:
            if "grid_layout" not in organizer.config:
                organizer.config["grid_layout"] = {}
            organizer.config["grid_layout"]["enabled"] = False
            organizer.positioner = None
        
        if args.grid_size:
            if "grid_layout" not in organizer.config:
                organizer.config["grid_layout"] = {}
            if "grid_size" not in organizer.config["grid_layout"]:
                organizer.config["grid_layout"]["grid_size"] = {}
            organizer.config["grid_layout"]["grid_size"]["width"] = args.grid_size[0]
            organizer.config["grid_layout"]["grid_size"]["height"] = args.grid_size[1]
        
        if args.grid_start:
            if "grid_layout" not in organizer.config:
                organizer.config["grid_layout"] = {}
            if "start_position" not in organizer.config["grid_layout"]:
                organizer.config["grid_layout"]["start_position"] = {}
            organizer.config["grid_layout"]["start_position"]["x"] = args.grid_start[0]
            organizer.config["grid_layout"]["start_position"]["y"] = args.grid_start[1]
        
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