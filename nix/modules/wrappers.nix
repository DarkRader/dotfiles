{ config, lib, userHome ? "/Users/${config.system.primaryUser}", ... }:
let
  userApp = name: "${userHome}/Applications/${lib.removeSuffix ".app" name}.app";

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
  options = {
    systemAppWrappers = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ "Safari" ];
      description = "List of protected macOS system apps to wrap in ~/Applications (e.g. 'Safari', 'App Store', 'System Settings')";
    };
  };

  config = {
    _module.args = {
      inherit userApp;
    };

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
      '';
    };
  };
}
