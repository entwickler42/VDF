#!/usr/bin/env python3
"""
Example script demonstrating the updated Steam macOS Shortcut Creator
with multiple app bundles and cache clearing.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Add parent directory to path to allow importing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from steam_macos_shortcut_creator.fixicons import (
    find_steam_users_dir,
    get_steam_user_dirs,
    find_shortcuts_file,
    get_app_info,
    create_shortcut,
    convert_icns_to_png,
    clear_steam_cache
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('steam-shortcuts')

def find_system_apps():
    """Find system apps that are likely to exist on most macOS installations."""
    common_apps = [
        '/System/Applications/Calculator.app',
        '/System/Applications/Calendar.app',
        '/System/Applications/Chess.app',
        '/System/Applications/Clock.app',
        '/System/Applications/Notes.app',
        '/System/Applications/Preview.app',
        '/System/Applications/TextEdit.app',
        '/Applications/Safari.app',
        '/Applications/Utilities/Terminal.app',
        '/Applications/Utilities/Activity Monitor.app',
        '/Applications/Utilities/Console.app',
        '/Applications/Utilities/Disk Utility.app',
        '/Applications/App Store.app',
        '/Applications/Books.app',
        '/Applications/Maps.app',
        '/Applications/Photos.app',
        '/Applications/Music.app',
        '/Applications/TV.app',
    ]
    
    # Return only those that exist
    return [app for app in common_apps if Path(app).exists()]

def main():
    """Test adding multiple app bundles at once."""
    # Find system apps that are likely to exist
    valid_paths = find_system_apps()
    
    if not valid_paths:
        logger.error("Could not find any common macOS applications to test with.")
        return 1
    
    # Limit to 3 apps for testing
    valid_paths = valid_paths[:3]
    logger.info(f"Found {len(valid_paths)} valid apps to test with:")
    for app in valid_paths:
        logger.info(f"- {app}")
    
    # Find Steam directory
    try:
        userdata_dir, steam_dir = find_steam_users_dir()
        logger.info(f"Steam directory: {steam_dir}")
    except SystemExit:
        logger.warning("Steam directory not found. This is just a test, so continuing anyway.")
        logger.info("Icons will be saved to your Desktop for verification.")
        steam_dir = None
        userdata_dir = None
    
    # Process each app to test icon extraction
    for app_path in valid_paths:
        logger.info(f"\nProcessing: {app_path}")
        
        # Get app info
        app_info = get_app_info(app_path)
        if not app_info:
            logger.error(f"Could not get app info for: {app_path}")
            continue
        
        logger.info(f"App name: {app_info['name']}")
        logger.info(f"Executable: {app_info['executable']}")
        logger.info(f"Icon path: {app_info['icon_path'] or 'No icon found'}")
        
        # Convert icon directly to test
        if app_info['icon_path']:
            # Remove spaces from app name for filename
            safe_name = app_info['name'].replace(' ', '_')
            test_output = Path.home() / f"Desktop/{safe_name}_icon.png"
            result = convert_icns_to_png(app_info['icon_path'], test_output, size=128)
            if result:
                logger.info(f"Test icon saved to: {test_output}")
                
                # Try to open the icon to verify
                try:
                    subprocess.run(['open', test_output])
                except:
                    pass
    
    # Clear Steam cache
    if steam_dir:
        logger.info("\nClearing Steam HTTP cache...")
        clear_steam_cache(steam_dir)
    
    logger.info("\nTest complete!")
    logger.info("To add these apps to Steam for real, run:")
    logger.info(f"steam-shortcuts {' '.join(f'"{path}"' for path in valid_paths)} --clear-cache")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 