#!/bin/bash
# Example script to add popular macOS games to Steam

# Ensure script is run from the virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "This script should be run from the virtual environment."
    echo "Run 'source .venv/bin/activate' first."
    exit 1
fi

# Function to add an app to Steam
add_to_steam() {
    local app_path="$1"
    if [[ -d "$app_path" ]]; then
        echo "Adding $app_path to Steam..."
        steam-shortcuts "$app_path" --size 256
    else
        echo "Warning: $app_path not found"
    fi
}

# Search for games in the Applications folder
echo "Looking for games in /Applications..."

# List of common game paths to check
GAME_PATHS=(
    "/Applications/Steam.app/Contents/MacOS/GameOverlayUI.app"
    "/Applications/Battle.net.app"
    "/Applications/Epic Games Launcher.app"
    "/Applications/Minecraft.app"
    "/Applications/League of Legends.app"
    "/Applications/Origin.app"
    "/Applications/Blizzard App.app"
)

# Add each game if it exists
for game in "${GAME_PATHS[@]}"; do
    add_to_steam "$game"
done

echo ""
echo "To find more applications to add, use the find-steam-apps command:"
echo "find-steam-apps game"
echo ""
echo "Remember to restart Steam to see your new shortcuts!" 