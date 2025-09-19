#!/usr/bin/env python3
"""
Demo script to visualize grid positioning calculations
"""

from desktop_organizer import DesktopOrganizer
from pathlib import Path

def demo_grid_positions():
    """Demonstrate grid positioning with sample items"""
    
    # Create organizer with grid layout enabled
    organizer = DesktopOrganizer()
    organizer.config["grid_layout"]["enabled"] = True
    
    # Sample items for demonstration
    sample_items = {
        "Gaming Tools": ["OBS Studio", "TrackIR", "Stream Deck", "Discord", "Gyazo"],
        "Games": ["Steam", "Epic Games", "Ubisoft Connect"],
        "Media Tools": ["Chrome", "Firefox", "Adobe Acrobat", "Spotify"],
        "Coding Tools": ["Visual Studio Code", "Docker Desktop", "Cygwin Terminal"],
        "Hacking Tools": ["Wireshark", "Nmap"],
        "Work Tools": ["NordVPN", "TeamViewer", "Oracle VirtualBox"],
        "Computer System": ["NVIDIA App", "Logitech G HUB"]
    }
    
    print("Grid Layout Positioning Demo")
    print("=" * 50)
    print(f"Grid Size: {organizer.config['grid_layout']['grid_size']['width']}x{organizer.config['grid_layout']['grid_size']['height']}")
    print(f"Start Position: ({organizer.config['grid_layout']['start_position']['x']}, {organizer.config['grid_layout']['start_position']['y']})")
    print(f"Max Columns: {organizer.config['grid_layout']['max_columns']}")
    print()
    
    for category, items in sample_items.items():
        print(f"{category}:")
        print("-" * (len(category) + 1))
        
        for index, item in enumerate(items):
            x, y = organizer.calculate_grid_position(category, index)
            print(f"  {item:<20} -> ({x:>3}, {y:>3})")
        
        print()
    
    # Visual representation
    print("Visual Grid Layout (approximate):")
    print("=" * 50)
    
    # Create a simple ASCII representation
    grid_visual = {}
    for category, items in sample_items.items():
        for index, item in enumerate(items):
            x, y = organizer.calculate_grid_position(category, index)
            # Normalize to grid cells for display
            grid_x = x // 100
            grid_y = y // 100
            if grid_y not in grid_visual:
                grid_visual[grid_y] = {}
            grid_visual[grid_y][grid_x] = item[:8]  # First 8 chars
    
    # Print the grid
    max_y = max(grid_visual.keys()) if grid_visual else 0
    max_x = max(max(row.keys()) for row in grid_visual.values()) if grid_visual else 0
    
    for y in range(max_y + 1):
        line = ""
        for x in range(max_x + 1):
            if y in grid_visual and x in grid_visual[y]:
                line += f"{grid_visual[y][x]:<10}"
            else:
                line += " " * 10
        print(line.rstrip())

if __name__ == "__main__":
    demo_grid_positions()