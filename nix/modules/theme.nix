{ config, lib, pkgs, userHome ? "/Users/${config.system.primaryUser}", ... }:
let
  theme = config.theme.icons;
  getIcon = name:
    let
      target = ../icons + "/${theme}/${name}.icns";
      fallback = ../icons/light + "/${name}.icns";
    in
      if builtins.pathExists target then target else fallback;
in
{
  options = {
    theme.icons = lib.mkOption {
      type = lib.types.str;
      default = "light";
      description = "Icon theme subfolder under nix/icons ('light', 'dark', etc.)";
    };

    theme.wallpaper = lib.mkOption {
      type = lib.types.nullOr (lib.types.either lib.types.path lib.types.str);
      default = null;
      description = "Path to desktop wallpaper image file (.heic, .png, .jpg)";
    };
  };

  config = {
    _module.args = {
      inherit getIcon;
    };

    assertions = [
      {
        assertion =
          config.theme.wallpaper == null
          || builtins.isPath config.theme.wallpaper
          || (builtins.isString config.theme.wallpaper && lib.hasPrefix "/" config.theme.wallpaper);
        message = "theme.wallpaper: Relative string paths (e.g. \"../wallpapers/...\") are not supported. Write it as an unquoted Nix path (e.g. ../wallpapers/silver-dark.jpg) so Nix can copy it into the Nix store.";
      }
    ];

    environment.systemPackages = [
      pkgs.desktoppr
    ];

    system.activationScripts.postActivation.text = lib.optionalString (config.theme.wallpaper != null) ''
      # Apply desktop wallpaper
      PRIMARY_USER="${config.system.primaryUser}"
      WALLPAPER="${toString config.theme.wallpaper}"
      USER_HOME="${userHome}"
      if [[ -f "$WALLPAPER" ]]; then
        echo "applying desktop wallpaper ($WALLPAPER)..."
        INDEX_PLIST="$USER_HOME/Library/Application Support/com.apple.wallpaper/Store/Index.plist"
        /usr/bin/python3 - <<'EOF' "$INDEX_PLIST" "$WALLPAPER"
import sys, os, plistlib, datetime

path = sys.argv[1]
wallpaper_path = sys.argv[2]

try:
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = plistlib.load(f)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {"SystemDefault": {"Type": "individual"}, "Displays": {}, "Spaces": {}}

    config_bytes = plistlib.dumps({
        "type": "imageFile",
        "url": {"relative": f"file://{wallpaper_path}"}
    }, fmt=plistlib.FMT_BINARY)

    now = datetime.datetime.now()
    desktop_dict = {
        "Content": {
            "Choices": [{
                "Provider": "com.apple.wallpaper.choice.image",
                "Files": [],
                "Configuration": config_bytes
            }],
            "Shuffle": "$null",
            "EncodedOptionValues": "$null"
        },
        "LastSet": now,
        "LastUse": now
    }

    if "SystemDefault" not in data:
        data["SystemDefault"] = {"Type": "individual"}
    data["SystemDefault"]["Desktop"] = desktop_dict

    for disp_val in data.get("Displays", {}).values():
        disp_val["Desktop"] = desktop_dict

    for sp_val in data.get("Spaces", {}).values():
        if "Default" in sp_val:
            sp_val["Default"]["Desktop"] = desktop_dict
        if "Displays" in sp_val:
            for disp_val in sp_val["Displays"].values():
                disp_val["Desktop"] = desktop_dict

    with open(path, "wb") as f:
        plistlib.dump(data, f, fmt=plistlib.FMT_BINARY)
except Exception as e:
    print(f"warning: failed to update Index.plist: {e}")
EOF
        chown "$PRIMARY_USER" "$INDEX_PLIST" 2>/dev/null || true
        killall WallpaperAgent 2>/dev/null || true
        launchctl asuser "$(id -u -- "$PRIMARY_USER")" sudo --user="$PRIMARY_USER" -- ${pkgs.desktoppr}/bin/desktoppr "$WALLPAPER" 2>/dev/null || true
      else
        echo "warning: Wallpaper file not found: $WALLPAPER" >&2
      fi
    '';
  };
}
