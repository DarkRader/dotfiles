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

3. **Declarative Icon Mapping (`nix/shared.nix` or `nix/personal/default.nix`)**:
   Icons are placed in `nix/icons/light/*.icns` and linked to their target applications:
   ```nix
   environment.customIcons = {
     enable = true;
     icons = [
       {
         path = "/Applications/Spark Desktop.app";
         icon = ./icons/light/spark.icns;
       }
       {
         path = "/Applications/TickTick.app";
         icon = ./icons/light/ticktick.icns;
       }
     ];
   };
   ```

## How It Executes During Activation

* `nix-darwin-custom-icons` injects an activation script in `system.activationScripts.extraActivation`.
* It uses macOS Cocoa `NSWorkspace.sharedWorkspace.setIcon(_:forFile:options:)` with `options: 2` (`NSExcludeQuickDrawElementsIconCreationOption`).
* Because the activation script runs during `darwin-rebuild switch` (which runs as root), it can set icons for both user-owned apps and root-owned Homebrew cask apps without permission errors.
* The script creates the `Icon\r` resource file and sets the `kHasCustomIcon` attribute without modifying the app's internal binaries or breaking code signing (`codesign`).
