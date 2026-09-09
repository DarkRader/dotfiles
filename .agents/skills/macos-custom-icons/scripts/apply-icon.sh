#!/usr/bin/env bash
# apply-icon.sh
# Safely applies a custom macOS icon (.icns) to an application bundle without breaking code signatures.

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <app_path> <icns_path> [--no-dock-restart]"
  echo "Example: $0 '/Applications/TickTick.app' '~/dotfiles/nix/icons/light/ticktick.icns'"
  exit 1
fi

APP_PATH="$1"
ICNS_PATH="$2"
RESTART_DOCK=true

if [ "${3:-}" = "--no-dock-restart" ]; then
  RESTART_DOCK=false
fi

# Expand paths
APP_PATH=$(python3 -c "import os, sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))" "$APP_PATH")
ICNS_PATH=$(python3 -c "import os, sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))" "$ICNS_PATH")

if [ ! -d "$APP_PATH" ]; then
  echo "Error: Application bundle not found at '$APP_PATH'" >&2
  exit 1
fi

if [ ! -f "$ICNS_PATH" ]; then
  echo "Error: Icon file not found at '$ICNS_PATH'" >&2
  exit 1
fi

echo "Applying '$ICNS_PATH' to '$APP_PATH'..."

RESULT=$(osascript <<SCRIPT
use framework "Cocoa"
set iconPath to "$ICNS_PATH"
set destPath to "$APP_PATH"
set imageData to (current application's NSImage's alloc()'s initWithContentsOfFile:iconPath)
return (current application's NSWorkspace's sharedWorkspace()'s setIcon:imageData forFile:destPath options:2)
SCRIPT
)

if [ "$RESULT" = "true" ]; then
  touch "$APP_PATH"
  echo "Successfully applied icon to $APP_PATH."
  if [ "$RESTART_DOCK" = true ]; then
    killall Dock 2>/dev/null || true
    echo "Restarted Dock."
  fi
else
  echo "Failed to set icon. If the app is owned by root, run with sudo." >&2
  exit 1
fi
