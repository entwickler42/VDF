# Steam macOS Shortcut Creator

A tool to add macOS applications to Steam with proper icons. This script automatically extracts app icons from macOS .app bundles, converts them to PNG format, and creates shortcuts in Steam.

## Features

- Creates Steam shortcuts for macOS .app bundles
- Automatically extracts app icons from Info.plist
- Converts .icns icons to PNG format with customizable size
- Saves icons to a dedicated folder in your Steam user directory
- Supports multiple Steam user accounts
- Handles duplicate shortcuts with overwrite option
- Creates new shortcuts.vdf file if needed
- **Add multiple app bundles at once**
- **Clears Steam's HTTP cache to ensure icons appear properly**
- **Fixes VDF serialization issues with large app IDs**
- **Uses the correct executable path format for macOS app bundles**

## Usage

After installation, you can use the command-line tool:

```bash
# If using the development environment
source .venv/bin/activate
steam-shortcuts /Applications/YourApp.app
```

Or run the module directly:

```bash
python -m steam_macos_shortcut_creator.fixicons /Applications/YourApp.app
```

To add multiple apps at once:

```bash
steam-shortcuts /Applications/App1.app /Applications/App2.app /Applications/App3.app
```

This will:
1. Extract each app's icon
2. Convert it to a 128x128 PNG
3. Save it to your Steam user directory
4. Create shortcuts in Steam for each app

## Command-line Options

| Option | Description |
|--------|-------------|
| `app_paths` | One or more paths to macOS app bundles (.app) |
| `--user USER_ID` | Steam user ID (if not specified, first user is used) |
| `--size SIZE` | PNG icon size in pixels (default: 128) |
| `--debug` | Show detailed debug information |
| `--overwrite` | Overwrite existing shortcut if it exists |
| `--new-vdf` | Create a new shortcuts.vdf file (ignore existing) |
| `--clear-cache` | Clear Steam's HTTP cache to ensure icons appear properly |

## Examples

Add multiple apps:
```bash
steam-shortcuts /Applications/App1.app /Applications/App2.app /Applications/App3.app
```

Convert with a larger icon:
```bash
steam-shortcuts /Applications/YourApp.app --size 256
```

Specify a Steam user:
```bash
steam-shortcuts /Applications/YourApp.app --user 12345678
```

Replace existing shortcuts and clear cache:
```bash
steam-shortcuts /Applications/YourApp.app --overwrite --clear-cache
```

Create a fresh shortcuts.vdf file:
```bash
steam-shortcuts /Applications/YourApp.app --new-vdf
```

Debug mode:
```bash
steam-shortcuts /Applications/YourApp.app --debug
```

## How It Works

1. The script locates the user's Steam shortcuts.vdf file
2. Extracts information from the macOS app bundle(s)
3. Finds the app's icon in its Resources directory
4. Converts the .icns icon to PNG format
5. Saves the PNG to a dedicated folder in the Steam directory
6. Creates a shortcut entry in the shortcuts.vdf file
7. Optionally clears Steam's HTTP cache to ensure icons appear properly

## Troubleshooting

- If icons don't appear in Steam, try using the `--clear-cache` option and restart Steam
- If shortcuts don't launch, verify the app path is correct
- If a shortcut doesn't launch, try adding it manually in Steam to see if there's a difference in how Steam handles it
- Completely quit and restart Steam after adding shortcuts (don't just close the window)
- Use `--debug` for more detailed information
- Run with `--new-vdf` if your shortcuts.vdf becomes corrupted
- If you encounter a "struct.error" about integer range, try running with `--new-vdf` to create a fresh shortcuts file (this has been fixed in the latest version)

## Technical Details

When adding shortcuts, this tool matches Steam's own format for app bundle references:

- The executable (`exe`) is set to the full path of the `.app` bundle with single quotes (e.g., `'/Applications/AppName.app'`)
- The working directory (`StartDir`) is set to the parent directory with single quotes (e.g., `'/Applications'`)

This matches how Steam adds shortcuts manually and ensures proper launching of the applications, especially for paths containing spaces or special characters.

## Development

To contribute to this project:

1. Fork the repository
2. Create a virtual environment: `python3 -m venv .venv`
3. Activate it: `source .venv/bin/activate`
4. Install dev dependencies: `pip install -e .`
5. Make your changes
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 