#!/usr/bin/env python3
"""
Demo script to visualize different alignment presets and folder positioning
"""

from desktop_organizer import DesktopOrganizer, WindowsDesktopPositioner
from pathlib import Path

def demo_alignment_presets():
    """Demonstrate different alignment presets"""
    
    # Create organizer with grid layout enabled
    organizer = DesktopOrganizer()
    organizer.config["grid_layout"]["enabled"] = True
    
    # Initialize positioner to get monitor info
    try:
        organizer.positioner = WindowsDesktopPositioner()
        monitor_width, monitor_height = organizer.positioner.get_monitor_info()
        usable_area = organizer.positioner.get_usable_desktop_area()
        print(f"Monitor Resolution: {monitor_width}x{monitor_height}")
        print(f"Usable Desktop Area: {usable_area[2]}x{usable_area[3]} (excluding taskbar)")
    except Exception as e:
        print(f"Could not get monitor info: {e}")
        return
    
    # Sample items including folders
    sample_items = {
        "Gaming Tools": [("OBS Studio", False), ("TrackIR", False), ("My Games Folder", True)],
        "Media Tools": [("Chrome", False), ("Documents Folder", True), ("Spotify", False)],
        "Coding Tools": [("Visual Studio Code", False), ("Projects Folder", True)],
        "Work Tools": [("NordVPN", False), ("Work Files", True)]
    }
    
    alignments = ["adaptive", "left", "right", "top", "bottom", "center", "corners"]
    
    for alignment in alignments:
        print(f"\n{'='*60}")
        print(f"ALIGNMENT: {alignment.upper()}")
        print(f"{'='*60}")
        
        # Set alignment in config
        organizer.config["grid_layout"]["alignment"] = alignment
        organizer.config["grid_layout"]["include_folders"] = True
        
        for category, items in sample_items.items():
            print(f"\n{category}:")
            print("-" * (len(category) + 1))
            
            for index, (item_name, is_folder) in enumerate(items):
                x, y = organizer.calculate_adaptive_grid_position(category, index, is_folder)
                folder_indicator = " 📁" if is_folder else " 📄"
                print(f"  {item_name:<20}{folder_indicator} -> ({x:>4}, {y:>4})")

def demo_folder_options():
    """Demonstrate folder inclusion/exclusion"""
    
    organizer = DesktopOrganizer()
    organizer.config["grid_layout"]["enabled"] = True
    
    try:
        organizer.positioner = WindowsDesktopPositioner()
    except Exception:
        return
    
    # Sample items with folders
    sample_items = {
        "Gaming Tools": [("OBS Studio", False), ("Games Folder", True), ("TrackIR", False)],
        "Work Tools": [("Documents", True), ("NordVPN", False), ("Projects", True)]
    }
    
    print(f"\n{'='*60}")
    print("FOLDER POSITIONING OPTIONS")
    print(f"{'='*60}")
    
    for include_folders in [True, False]:
        status = "ENABLED" if include_folders else "DISABLED"
        print(f"\nFolder Positioning: {status}")
        print("-" * 30)
        
        organizer.config["grid_layout"]["include_folders"] = include_folders
        organizer.config["grid_layout"]["alignment"] = "adaptive"
        
        for category, items in sample_items.items():
            print(f"\n{category}:")
            for index, (item_name, is_folder) in enumerate(items):
                x, y = organizer.calculate_adaptive_grid_position(category, index, is_folder)
                folder_indicator = " 📁" if is_folder else " 📄"
                print(f"  {item_name:<15}{folder_indicator} -> ({x:>4}, {y:>4})")

if __name__ == "__main__":
    print("Desktop Grid Alignment & Folder Positioning Demo")
    print("=" * 60)
    
    demo_alignment_presets()
    demo_folder_options()
    
    print(f"\n{'='*60}")
    print("USAGE EXAMPLES:")
    print(f"{'='*60}")
    print("python desktop_organizer.py --grid --align left")
    print("python desktop_organizer.py --grid --align center --include-folders") 
    print("python desktop_organizer.py --grid --align right --no-folders")
    print("python desktop_organizer.py --grid --align bottom")
    print("python desktop_organizer.py --grid --align corners")