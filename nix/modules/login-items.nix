{ config, lib, ... }:
let
  loginItemSubmodule = lib.types.submodule {
    options = {
      path = lib.mkOption {
        type = lib.types.str;
        description = "Path to application bundle (.app) or executable";
      };
      hidden = lib.mkOption {
        type = lib.types.bool;
        default = false;
        description = "Whether to hide the application window upon login";
      };
      name = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Custom display name (defaults to app bundle name)";
      };
    };
  };

  normalizedItems = map (item:
    if builtins.isString item then {
      path = item;
      hidden = false;
      name = null;
    } else item
  ) config.loginItems;

  itemsJson = builtins.toJSON normalizedItems;
in
{
  options = {
    loginItems = lib.mkOption {
      type = lib.types.listOf (lib.types.either lib.types.str loginItemSubmodule);
      default = [ ];
      description = "List of applications to automatically launch at login (macOS Open at Login)";
      example = [
        "/Applications/Raycast.app"
        "/Applications/OrbStack.app"
        {
          path = "/Applications/Warp.app";
          hidden = true;
        }
      ];
    };
  };

  config = lib.mkIf (config.loginItems != [ ]) {
    system.activationScripts.postActivation.text = ''
      # Configure user login items (Open at Login)
      PRIMARY_USER="${config.system.primaryUser}"
      ITEMS_JSON='${itemsJson}'

      echo "configuring login items for $PRIMARY_USER..."
      launchctl asuser "$(id -u -- "$PRIMARY_USER")" sudo --user="$PRIMARY_USER" -- /usr/bin/python3 - <<'EOF' "$ITEMS_JSON"
import sys, json, os, subprocess

try:
    target_items = json.loads(sys.argv[1])
except Exception as e:
    sys.exit(f"Error parsing login items JSON: {e}")

get_script = """
tell application "System Events"
    set itemData to {}
    repeat with anItem in login items
        try
            set end of itemData to (name of anItem & "|||" & path of anItem)
        end try
    end repeat
    set AppleScript's text item delimiters to "%%%"
    return itemData as string
end tell
"""

try:
    res = subprocess.run(["osascript", "-e", get_script], capture_output=True, text=True, check=True)
    raw = res.stdout.strip().split("%%%") if res.stdout.strip() else []
    current_items = []
    for entry in raw:
        parts = entry.split("|||")
        if len(parts) == 2:
            current_items.append({"name": parts[0].strip(), "path": parts[1].strip()})
except Exception as e:
    print(f"warning: could not query current login items: {e}")
    current_items = []

def is_already_registered(target_path, current):
    t_base = os.path.basename(target_path.rstrip("/")).lower()
    t_real = os.path.realpath(target_path) if os.path.exists(target_path) else target_path
    for c in current:
        c_path = c["path"]
        if c_path == target_path:
            return True
        if os.path.basename(c_path.rstrip("/")).lower() == t_base:
            return True
        if os.path.exists(c_path) and os.path.realpath(c_path) == t_real:
            return True
    return False

for item in target_items:
    target_path = item.get("path")
    if not target_path:
        continue

    # Resolve home relative paths if any
    target_path = os.path.expanduser(target_path)

    if is_already_registered(target_path, current_items):
        continue

    if not os.path.exists(target_path):
        print(f"warning: login item target does not exist on disk: {target_path}")
        continue

    is_hidden = "true" if item.get("hidden", False) else "false"
    item_name = item.get("name") or os.path.splitext(os.path.basename(target_path))[0]

    add_script = """
    tell application "System Events"
        make login item at end with properties {path: "%s", hidden: %s}
    end tell
    """ % (target_path, is_hidden)
    try:
        subprocess.run(["osascript", "-e", add_script], check=True, capture_output=True)
        print("added login item: " + item_name + " (" + target_path + ")")
    except Exception as e:
        print("warning: failed to add login item " + target_path + ": " + str(e))
EOF
    '';
  };
}
