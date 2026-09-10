{ config, lib, pkgs, userHome ? "/Users/${config.system.primaryUser}", ... }:
let
  theme = config.theme.icons;
  getIcon = name:
    let
      target = ./icons + "/${theme}/${name}.icns";
      fallback = ./icons/light + "/${name}.icns";
    in
      if builtins.pathExists target then target else fallback;
  userApp = name: "${userHome}/Applications/${lib.removeSuffix ".app" name}.app";
in
{
  options = {
    theme.icons = lib.mkOption {
      type = lib.types.str;
      default = "light";
      description = "Icon theme subfolder under nix/icons ('light', 'dark', etc.)";
    };

    systemAppWrappers = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ "Safari" ];
      description = "List of protected macOS system apps to wrap in ~/Applications (e.g. 'Safari', 'App Store', 'System Settings')";
    };

    theme.wallpaper = lib.mkOption {
      type = lib.types.nullOr (lib.types.either lib.types.path lib.types.str);
      default = null;
      description = "Path to desktop wallpaper image file (.heic, .png, .jpg)";
    };
  };

  config =
    let
      userAppsPrefix = "${userHome}/Applications/";

      getDockPath = a:
        if builtins.isAttrs a then (a.tile-data.file-data._CFURLString or "")
        else if builtins.isString a then a
        else "";

      dockApps = config.system.defaults.dock.persistent-apps or [ ];
      dockPaths = map getDockPath dockApps;
      appNamesFromDock = map
        (p: lib.removeSuffix ".app" (lib.removePrefix userAppsPrefix p))
        (lib.filter (p: lib.hasPrefix userAppsPrefix p) dockPaths);

      customIconApps = config.environment.customIcons.icons or [ ];
      appNamesFromIcons = map
        (item: lib.removeSuffix ".app" (lib.removePrefix userAppsPrefix item.path))
        (lib.filter (item: lib.hasPrefix userAppsPrefix item.path) customIconApps);

      allAppsToWrap = lib.unique (
        (map (lib.removeSuffix ".app") config.systemAppWrappers)
        ++ appNamesFromDock
        ++ appNamesFromIcons
      );
    in
    {
      _module.args = {
        inherit getIcon userApp;
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
    # Editor
    pkgs.neovim

    # Core CLI and repository tools
    pkgs.git
    pkgs.gh
    pkgs.stow

    # Shell and terminal
    pkgs.starship
    pkgs.eza
    pkgs.tmux
    pkgs.zsh-syntax-highlighting
    pkgs.desktoppr

    # Languages and package managers
    pkgs.python313Packages.pygments
    pkgs.pnpm
    pkgs.nodejs
    pkgs.uv

    # Development tools
    pkgs.nixd
    pkgs.nil
    pkgs.mas
    pkgs.pre-commit
    pkgs.skills

    # Media and system tools
    pkgs.ffmpeg
    pkgs.htop
  ];

  system.stateVersion = 6;
  nixpkgs.hostPlatform = "aarch64-darwin";

  nix.settings.experimental-features = "nix-command flakes";

  system.activationScripts = {
    preActivation.text = ''
      # Set up wrappers for protected macOS system apps in user's ~/Applications
      USER_HOME="${userHome}"
      PRIMARY_USER="${config.system.primaryUser}"

      mkdir -p "$USER_HOME/Applications"

      ${lib.concatMapStringsSep "\n" (app: ''
        APP_RAW="${app}"
        if [[ "$APP_RAW" = /* ]]; then
          SRC_CANDIDATE="$APP_RAW"
          APP_NAME="$(basename "$APP_RAW" .app)"
          SRC=""
          if [[ -d "$SRC_CANDIDATE/Contents" ]]; then
            SRC="$SRC_CANDIDATE/Contents"
          fi
        else
          APP_NAME="''${APP_RAW%.app}"
          SRC=""
          for candidate in \
            "/Applications/$APP_NAME.app" \
            "/System/Applications/$APP_NAME.app" \
            "/System/Applications/Utilities/$APP_NAME.app" \
            "/System/Cryptexes/App/System/Applications/$APP_NAME.app"; do
            if [[ -d "$candidate/Contents" ]]; then
              SRC="$candidate/Contents"
              break
            fi
          done
        fi

        if [[ -n "$SRC" ]]; then
          TARGET_APP="$USER_HOME/Applications/$APP_NAME.app"
          mkdir -p "$TARGET_APP"
          ln -sfn "$SRC" "$TARGET_APP/Contents"
          chown -R "$PRIMARY_USER" "$TARGET_APP"
          /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$TARGET_APP" 2>/dev/null || true
        else
          echo "warning: Could not find system source for $APP_RAW" >&2
        fi
      '') allAppsToWrap}
    '';

    postActivation.text = ''
      # Ensure user ownership of custom icons inside system app wrappers
      ${lib.concatMapStringsSep "\n" (app: ''
        APP_NAME="$(basename "${app}" .app)"
        TARGET_APP="${userHome}/Applications/$APP_NAME.app"
        if [[ -d "$TARGET_APP" ]]; then
          chown -R "${config.system.primaryUser}" "$TARGET_APP" 2>/dev/null || true
        fi
      '') allAppsToWrap}

      ${lib.optionalString (config.theme.wallpaper != null) ''
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
      ''}
    '';
  };

  environment.customIcons = {
    enable = true;
    icons = [
      {
        path = userApp "Safari";
        icon = getIcon "safari";
      }
      {
        path = "/Applications/Spark Desktop.app";
        icon = getIcon "spark";
      }
      {
        path = "/Applications/Obsidian.app";
        icon = getIcon "obsidian";
      }
      {
        path = "/Applications/Spotify.app";
        icon = getIcon "spotify";
      }
      {
        path = "/Applications/Telegram.app";
        icon = getIcon "telegram";
      }
      {
        path = "/Applications/Zed.app";
        icon = getIcon "zed";
      }
      {
        path = "/Applications/Warp.app";
        icon = getIcon "warp";
      }
      {
        path = "/Applications/TickTick.app";
        icon = getIcon "ticktick";
      }
      {
        path = "/Applications/Notion Calendar.app";
        icon = getIcon "notion-calendar";
      }
    ];
  };

  system.defaults = {
    NSGlobalDomain = {
      AppleInterfaceStyle = "Dark";
      # Finder sidebar icon size:
      # 1 = small, 2 = medium, 3 = large
      NSTableViewDefaultSizeMode = 2;
    };

    dock = {
      magnification = true;
      mineffect = "scale";
      minimize-to-application = true;
      autohide = true;
      show-recents = false;
    };

    finder = {
      FXPreferredViewStyle = "clmv";
      _FXSortFoldersFirst = true;
      NewWindowTarget = "Home";
      AppleShowAllExtensions = true;
    };

    trackpad = {
      Clicking = true;
      TrackpadRightClick = true;
    };

    CustomUserPreferences = {
      "com.apple.assistant.support" = {
        "Assistant Enabled" = false;
      };
      "com.apple.assistant.backedup" = {
        "Assistant Enabled" = false;
      };
      "com.apple.Siri" = {
        "StatusMenuVisible" = false;
        "UserHasDeclinedEnable" = true;
      };
    };
  };

  homebrew = {
    enable = true;

    onActivation = {
      autoUpdate = true;
      upgrade = true;
      cleanup = "zap";
    };

    taps = [
      "hashicorp/tap"
    ];

    # Infrastructure tools
    brews = [
      "hashicorp/tap/terraform"
      "hashicorp/tap/vault"
    ];

    # Desktop applications
    casks = [
      "antigravity-cli"
      "appcleaner"
      "claude"
      "codex"
      "font-jetbrains-mono-nerd-font"
      "hiddenbar"
      "obsidian"
      "orbstack"
      "postman"
      "postman-agent"
      "raycast"
      "readdle-spark"
      "spotify"
      "warp"
      "zed"
      "telegram"
      "notion-calendar"
      "ticktick"
    ];
  };
};
}
