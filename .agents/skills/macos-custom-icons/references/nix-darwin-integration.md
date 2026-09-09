# nix-darwin Custom Icons Integration

This document describes how custom application icons are declared and automatically applied in this dotfiles repository using the `nix-darwin-custom-icons` flake module.

## Architecture

1. **Flake Input (`nix/flake.nix`)**:
   ```nix
   inputs = {
     # ...
     darwin-custom-icons.url = "github:ryanccn/nix-darwin-custom-icons";
   };
   ```

2. **Module Inclusion (`nix/flake.nix`)**:
   The module `darwin-custom-icons.darwinModules.default` is added to `commonModules`:
   ```nix
   commonModules = user: [
     ./shared.nix
     nix-homebrew.darwinModules.nix-homebrew
     darwin-custom-icons.darwinModules.default
     # ...
   ];
   ```

3. **Declarative Icon Mapping & Theme Selection (`nix/shared.nix` and host profiles)**:
   Icons are organized into subfolders (`nix/icons/light/`, `nix/icons/dark/`).
   A custom `theme.icons` option defaults to `"light"`, and a `getIcon` helper dynamically resolves `./icons/${theme}/<name>.icns` with automatic fallback:
   ```nix
   # In nix/shared.nix:
   options.theme.icons = lib.mkOption {
     type = lib.types.str;
     default = "light";
     description = "Icon theme subfolder under nix/icons ('light', 'dark', etc.)";
   };

   environment.customIcons = {
     enable = true;
     icons = [
       {
         path = "/Applications/Spotify.app";
         icon = getIcon "spotify";
       }
     ];
   };
   ```

   In host profiles (e.g. `nix/personal/default.nix`):
   ```nix
   { getIcon, ... }:
   {
     # Override theme for this machine (defaults to "light" if omitted)
     theme.icons = "dark";

     environment.customIcons.icons = [
       {
         path = "/Applications/Discord.app";
         icon = getIcon "discord";
       }
     ];
   }
   ```

## How It Executes During Activation

* `nix-darwin-custom-icons` injects an activation script in `system.activationScripts.extraActivation`.
* It uses macOS Cocoa `NSWorkspace.sharedWorkspace.setIcon(_:forFile:options:)` with `options: 2` (`NSExcludeQuickDrawElementsIconCreationOption`).
* Because the activation script runs during `darwin-rebuild switch` (which runs as root), it can set icons for both user-owned apps and root-owned Homebrew cask apps without permission errors.
* The script creates the `Icon\r` resource file and sets the `kHasCustomIcon` attribute without modifying the app's internal binaries or breaking code signing (`codesign`).
