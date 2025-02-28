#!/usr/bin/env python3
"""
Steam macOS Shortcut Creator - Main implementation module

This module handles the extraction of icons from macOS app bundles,
conversion to PNG format, and creation of shortcuts in Steam.
"""

import os
import sys
import argparse
import logging
import subprocess
import plistlib
import vdf
import shutil
import struct
from pathlib import Path
from tempfile import NamedTemporaryFile
from PIL import Image
import binascii

# Set up logging
logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger('steam-shortcuts')

def find_steam_users_dir():
    """Find the Steam userdata directory."""
    home = Path.home()
    steam_dir = home / "Library/Application Support/Steam"
    userdata_dir = steam_dir / "userdata"
    
    if not userdata_dir.exists():
        logger.error(f"Could not find Steam userdata directory at {userdata_dir}")
        sys.exit(1)
    
    return userdata_dir, steam_dir

def get_steam_user_dirs(userdata_dir):
    """Get list of available Steam user directories."""
    user_dirs = [d for d in userdata_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    
    if not user_dirs:
        logger.error("No Steam user directories found")
        sys.exit(1)
    
    return user_dirs

def find_shortcuts_file(user_dir, create_new=False):
    """Find or create the shortcuts.vdf file for a Steam user."""
    config_dir = user_dir / "config"
    shortcuts_file = config_dir / "shortcuts.vdf"
    
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    
    if not shortcuts_file.exists() or create_new:
        # Create an empty shortcuts file
        with open(shortcuts_file, 'wb') as f:
            f.write(b'\x00shortcuts\x00\x08\x08')
        logger.info(f"Created new shortcuts file: {shortcuts_file}")
    
    return shortcuts_file

def get_app_info(app_path):
    """Extract information from a macOS app bundle."""
    app_path = Path(app_path).expanduser().resolve()
    
    if not app_path.exists():
        logger.error(f"App not found: {app_path}")
        return None
    
    if not app_path.is_dir() or not str(app_path).endswith('.app'):
        logger.error(f"Not a valid macOS app bundle: {app_path}")
        return None
    
    # Get app name and executable path
    info_plist_path = app_path / "Contents/Info.plist"
    if not info_plist_path.exists():
        logger.error(f"Info.plist not found in app bundle: {app_path}")
        return None
    
    with open(info_plist_path, 'rb') as f:
        info_plist = plistlib.load(f)
    
    app_name = info_plist.get('CFBundleName', app_path.stem)
    bundle_id = info_plist.get('CFBundleIdentifier', '')
    
    # Store both the app bundle path and the internal executable
    app_bundle_path = str(app_path)
    internal_executable = app_path / "Contents/MacOS" / info_plist.get('CFBundleExecutable', app_name)
    
    # Find the icon
    icon_name = info_plist.get('CFBundleIconFile', '')
    if not icon_name.endswith('.icns'):
        icon_name += '.icns'
    
    icon_path = app_path / "Contents/Resources" / icon_name
    
    if not icon_path.exists():
        # Try to find any .icns file in the Resources directory
        resources_dir = app_path / "Contents/Resources"
        icns_files = list(resources_dir.glob('*.icns'))
        if icns_files:
            icon_path = icns_files[0]
        else:
            logger.warning(f"No icon found for app: {app_path}")
            icon_path = None
    
    return {
        'name': app_name,
        'bundle_id': bundle_id,
        'app_bundle_path': app_bundle_path,  # The .app bundle path
        'executable': str(internal_executable),  # The internal executable (for reference)
        'icon_path': icon_path
    }

def convert_icns_to_png(icns_path, output_path, size=128):
    """Convert an .icns file to a PNG file with the specified size."""
    if not icns_path:
        return None
    
    try:
        # First try using sips (macOS built-in)
        with NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        subprocess.run([
            'sips',
            '-s', 'format', 'png',
            '--resampleHeightWidth', str(size), str(size),
            str(icns_path),
            '--out', temp_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Open and save with PIL to ensure proper format
        img = Image.open(temp_path)
        # Ensure RGBA mode for proper transparency
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Save the primary icon
        img.save(output_path, format='PNG')
        
        # Save all the grid image variants that Steam might look for
        grid_path = output_path.parent / f"{output_path.stem.replace('p', '')}.png"
        img.save(grid_path, format='PNG')
        
        # Save additional grid image variants (based on Steam's naming conventions)
        # _hero version (used for hero banners)
        hero_path = output_path.parent / f"{output_path.stem.replace('p', '')}_hero.png" 
        img.save(hero_path, format='PNG')
        
        # _logo version (used for logos)
        logo_path = output_path.parent / f"{output_path.stem.replace('p', '')}_logo.png"
        img.save(logo_path, format='PNG')
        
        # Also save to alternative locations that Steam might check
        # Try the userdata/[userid]/config/librarycache location as well
        try:
            library_cache_dir = output_path.parent.parent / "librarycache"
            library_cache_dir.mkdir(parents=True, exist_ok=True)
            
            library_icon_path = library_cache_dir / f"{output_path.stem.replace('p', '')}.png"
            img.save(library_icon_path, format='PNG')
        except Exception as e:
            logger.debug(f"Could not save icon to librarycache directory: {e}")
        
        os.unlink(temp_path)
        
        logger.debug(f"Icon converted and saved as multiple variants in {output_path.parent}")
        return output_path
    except Exception as e:
        logger.error(f"Error converting icon: {e}")
        return None

def create_shortcut(shortcuts_data, app_info, grid_dir, size=128, overwrite=False):
    """Create a shortcut in the shortcuts.vdf file."""
    if not app_info:
        return False
    
    # Use the app bundle path to match how Steam manually adds shortcuts
    app_path = app_info['app_bundle_path']
    
    # Generate a unique app ID based on the app bundle path
    # Use CRC32 but ensure it fits in a signed 32-bit integer to avoid VDF serialization issues
    crc_value = binascii.crc32(app_path.encode()) & 0xffffffff
    # If value is too large for signed 32-bit int, adjust it to fit
    if crc_value > 0x7FFFFFFF:  # 2147483647 (max signed 32-bit int)
        crc_value = crc_value & 0x7FFFFFFF
    app_id = str(crc_value)
    
    # Check if shortcut already exists
    if 'shortcuts' not in shortcuts_data:
        shortcuts_data['shortcuts'] = {}
    
    for existing_id, shortcut in shortcuts_data.get('shortcuts', {}).items():
        if shortcut.get('exe') == app_path:
            if not overwrite:
                logger.warning(f"Shortcut for {app_info['name']} already exists. Use --overwrite to replace it.")
                return False
            else:
                # Remove existing shortcut
                del shortcuts_data['shortcuts'][existing_id]
                break
    
    # Create grid directory if it doesn't exist
    grid_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to the PNG icon we'll generate (used for the VDF file)
    png_path = None
    
    # Convert icon to PNG
    if app_info['icon_path']:
        png_path = grid_dir / f"{app_id}p.png"
        if convert_icns_to_png(app_info['icon_path'], png_path, size):
            # Make sure we're using the absolute path for the PNG
            png_path = png_path.absolute()
            logger.info(f"Icon converted and saved to {png_path}")
    
    # Get the parent directory of the app bundle (typically /Applications)
    working_directory = Path(app_path).parent
    
    # Create shortcut entry with more Steam-specific fields
    shortcuts_data['shortcuts'][app_id] = {
        'appid': int(app_id),
        'AppName': app_info['name'],  # Ensure correct case for Steam
        'appname': app_info['name'],
        'Exe': f"'{app_path}'",  # Use the .app bundle path with single quotes
        'exe': f"'{app_path}'",  # Use the .app bundle path with single quotes
        'StartDir': f"'{str(working_directory)}'",  # Parent directory with single quotes
        'icon': str(png_path) if png_path else "",
        'shortcutpath': "",
        'LaunchOptions': "",
        'IsHidden': 0,
        'AllowDesktopConfig': 1,
        'AllowOverlay': 1,
        'OpenVR': 0,
        'Devkit': 0,
        'DevkitGameID': "",
        'LastPlayTime': 0,
        'FlatpakAppID': "",
        'tags': {}
    }
    
    return True

def clear_steam_cache(steam_dir):
    """Clear Steam's HTTP cache and other caches to ensure new icons are loaded."""
    # Clear HTTP cache
    http_cache_dir = steam_dir / "config/htmlcache"
    if http_cache_dir.exists():
        try:
            for item in http_cache_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            logger.info("Cleared Steam HTTP cache")
        except Exception as e:
            logger.warning(f"Failed to clear Steam HTTP cache: {e}")
    
    # Also clear the appcache to force Steam to reload all assets
    appcache_dir = steam_dir / "appcache"
    if appcache_dir.exists():
        try:
            # Only remove specific subdirectories that are safe to delete
            for subdir in ["httpcache", "stats"]:
                path = appcache_dir / subdir
                if path.exists():
                    for item in path.iterdir():
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
            logger.info("Cleared Steam appcache")
        except Exception as e:
            logger.warning(f"Failed to clear Steam appcache: {e}")
            
    # Clear the shader cache too
    shadercache_dir = steam_dir / "shadercache"
    if shadercache_dir.exists():
        try:
            # Just clean out the non-Steam app shader caches (those with numeric names)
            for item in shadercache_dir.iterdir():
                if item.is_dir() and item.name.isdigit():
                    shutil.rmtree(item)
            logger.info("Cleared Steam shader cache for non-Steam apps")
        except Exception as e:
            logger.warning(f"Failed to clear Steam shader cache: {e}")

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Create Steam shortcuts for macOS applications with proper icons"
    )
    parser.add_argument(
        "app_paths", 
        nargs='+',
        help="Paths to one or more macOS app bundles (.app)"
    )
    parser.add_argument(
        "--user", 
        help="Steam user ID (if not specified, first user is used)"
    )
    parser.add_argument(
        "--size", 
        type=int, 
        default=128, 
        help="PNG icon size in pixels (default: 128)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Show detailed debug information"
    )
    parser.add_argument(
        "--overwrite", 
        action="store_true", 
        help="Overwrite existing shortcut if it exists"
    )
    parser.add_argument(
        "--new-vdf", 
        action="store_true", 
        help="Create a new shortcuts.vdf file (ignore existing)"
    )
    parser.add_argument(
        "--clear-cache", 
        action="store_true", 
        help="Clear Steam's HTTP cache to ensure icons appear properly"
    )
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Set logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    # Find Steam userdata directory
    userdata_dir, steam_dir = find_steam_users_dir()
    logger.debug(f"Found Steam userdata directory: {userdata_dir}")
    
    # Get user directories
    user_dirs = get_steam_user_dirs(userdata_dir)
    logger.debug(f"Found {len(user_dirs)} Steam user directories")
    
    # Select user directory
    user_dir = None
    if args.user:
        for dir in user_dirs:
            if dir.name == args.user:
                user_dir = dir
                break
        if not user_dir:
            logger.error(f"Steam user ID {args.user} not found")
            sys.exit(1)
    else:
        user_dir = user_dirs[0]
    
    logger.debug(f"Using Steam user directory: {user_dir}")
    
    # Find shortcuts.vdf file
    shortcuts_file = find_shortcuts_file(user_dir, args.new_vdf)
    logger.debug(f"Using shortcuts file: {shortcuts_file}")
    
    # Load existing shortcuts
    try:
        with open(shortcuts_file, 'rb') as f:
            shortcuts_data = vdf.binary_load(f)
    except Exception as e:
        logger.warning(f"Could not load shortcuts file: {e}")
        shortcuts_data = {}
    
    # Create grid directory for icons
    grid_dir = user_dir / "config/grid"
    
    # Process each app path
    success_count = 0
    for app_path in args.app_paths:
        # Get app info
        app_info = get_app_info(app_path)
        if not app_info:
            continue
            
        logger.debug(f"App info: {app_info}")
        
        # Create shortcut
        if create_shortcut(shortcuts_data, app_info, grid_dir, args.size, args.overwrite):
            logger.info(f"Shortcut created for {app_info['name']}")
            success_count += 1
    
    # If any shortcuts were created successfully, save the file
    if success_count > 0:
        try:
            with open(shortcuts_file, 'wb') as f:
                vdf.binary_dump(shortcuts_data, f)
            
            logger.info(f"Successfully created {success_count} shortcut(s)")
            
            # Clear Steam's HTTP cache if requested
            if args.clear_cache:
                clear_steam_cache(steam_dir)
            
            logger.info("Restart Steam to see the shortcut(s) with their icons")
            logger.info("Note: You may need to restart Steam COMPLETELY (quit from the menu) for icons to appear")
        except struct.error as e:
            logger.error(f"Error saving shortcuts file: {e}")
            logger.error("This is likely due to an integer overflow issue in the VDF format.")
            backup_file = shortcuts_file.with_suffix('.vdf.bak')
            logger.info(f"Saving backup of original shortcuts file to {backup_file}")
            if shortcuts_file.exists():
                shutil.copy2(shortcuts_file, backup_file)
            return 1
        except Exception as e:
            logger.error(f"Error saving shortcuts file: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 