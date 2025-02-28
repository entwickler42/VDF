#!/usr/bin/env python3
"""
Simple test script for the Steam macOS Shortcut Creator
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("test-script")

# Add parent directory to path to allow importing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Simple test to verify logging and functionality."""
    logger.info("Starting simple test")
    
    # List some common macOS applications
    apps = [
        '/System/Applications/Calculator.app',
        '/Applications/Utilities/Terminal.app',
        '/Applications/Safari.app',
    ]
    
    # Check which ones exist
    exists = []
    for app in apps:
        path = Path(app)
        if path.exists():
            exists.append(app)
            logger.info(f"Found: {app}")
        else:
            logger.warning(f"Not found: {app}")
    
    logger.info(f"Found {len(exists)} out of {len(apps)} applications")
    
    # Import the module to test
    try:
        from steam_macos_shortcut_creator import fixicons
        logger.info("Successfully imported fixicons module")
        
        # Test getting app info for one app
        if exists:
            logger.info(f"Testing get_app_info on {exists[0]}")
            app_info = fixicons.get_app_info(exists[0])
            logger.info(f"App name: {app_info['name']}")
            logger.info(f"Executable: {app_info['executable']}")
            
            # Test icon conversion
            if app_info['icon_path']:
                logger.info(f"Icon path: {app_info['icon_path']}")
                test_output = Path.home() / f"Desktop/test_icon.png"
                result = fixicons.convert_icns_to_png(app_info['icon_path'], test_output, size=128)
                if result:
                    logger.info(f"Icon saved to: {test_output}")
            else:
                logger.warning("No icon found for the app")
    except Exception as e:
        logger.error(f"Error testing module: {e}")
    
    logger.info("Test completed")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 