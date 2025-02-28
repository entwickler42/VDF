#!/usr/bin/env python3
"""
Steam macOS Shortcut Creator - App finder utility

This script helps users find .app bundles on their macOS system
that they might want to add to Steam.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def find_apps(search_dirs=['/Applications', '~/Applications'], search_term=None):
    """
    Find .app bundles in the specified directories.
    
    Args:
        search_dirs: List of directories to search
        search_term: Optional search term to filter results
    
    Returns:
        List of found .app paths
    """
    apps = []
    
    for search_dir in search_dirs:
        search_dir = Path(search_dir).expanduser()
        
        if not search_dir.exists():
            print(f"Warning: Directory {search_dir} does not exist, skipping")
            continue
        
        # Use find to locate .app bundles
        try:
            cmd = ['find', str(search_dir), '-name', '*.app', '-type', 'd', '-maxdepth', '3']
            output = subprocess.check_output(cmd, text=True)
            found_apps = output.strip().split('\n')
            
            # Filter by search term if provided
            if search_term and search_term.strip():
                term = search_term.lower()
                found_apps = [app for app in found_apps if term in app.lower()]
            
            # Filter out empty entries
            found_apps = [app for app in found_apps if app]
            
            apps.extend(found_apps)
        
        except subprocess.CalledProcessError:
            print(f"Error searching in {search_dir}")
            continue
    
    return sorted(apps)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Find macOS application bundles (.app) for adding to Steam"
    )
    parser.add_argument(
        "--search-dirs",
        nargs="+",
        default=['/Applications', '~/Applications'],
        help="Directories to search for .app bundles (default: /Applications ~/Applications)"
    )
    parser.add_argument(
        "search_term",
        nargs="?",
        help="Optional search term to filter applications"
    )
    parser.add_argument(
        "--limit", 
        type=int,
        default=0,
        help="Limit the number of results (default: 0 = no limit)"
    )
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    print(f"Searching for .app bundles in: {', '.join(args.search_dirs)}")
    if args.search_term:
        print(f"Filtering by: {args.search_term}")
    
    apps = find_apps(args.search_dirs, args.search_term)
    
    if not apps:
        print("No matching applications found")
        return 1
    
    if args.limit > 0 and len(apps) > args.limit:
        print(f"\nFound {len(apps)} applications, showing first {args.limit}:\n")
        apps = apps[:args.limit]
    else:
        print(f"\nFound {len(apps)} applications:\n")
    
    for i, app in enumerate(apps, 1):
        print(f"{i}. {app}")
    
    print("\nTo add applications to Steam, use the steam-shortcuts command:")
    
    if len(apps) > 1:
        # Show example with first 3 apps (or all if less than 3)
        example_apps = apps[:min(3, len(apps))]
        example_cmd = "steam-shortcuts " + " ".join(f'"{app}"' for app in example_apps)
        print(example_cmd)
        print("\nYou can add multiple applications at once!")
    else:
        print(f'steam-shortcuts "{apps[0]}"')
    
    print("\nAdd --clear-cache to ensure icons appear properly in Steam:")
    print("steam-shortcuts [app paths] --clear-cache")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 