# Troubleshooting macOS Custom Icons

## 1. White Box Around Icon in Dock

* **Symptom**: The icon appears as an ugly solid white square on the Dock instead of a rounded squircle.
* **Cause**: QuickLook (`qlmanage`) or an image exporter filled the transparent padding outside the squircle with solid white `#FFFFFF`.
* **Fix**: Ensure the alpha channel outside the 824x824 squircle is 0. Use `icon_tool.py`, which automatically masks the icon using Cocoa graphics contexts before compiling with `iconutil`.

## 2. "Permission Denied" When Applying Icon

* **Symptom**: Running `osascript` fails with `false` or `touch: /Applications/<App>.app: Permission denied`.
* **Cause**: Applications installed via Homebrew Cask with `sudo` or `/Applications` installers may be owned by `root:wheel` or `root:admin`.
* **Fix**:
  * Option A: Run `darwin-rebuild switch`, which executes with root privileges during system activation.
  * Option B: Reclaim ownership for the current user:
    ```bash
    sudo chown -R $(whoami) "/Applications/<App>.app"
    ```

## 3. Icon Does Not Update in Dock / Stale Icon Cache

* **Symptom**: The icon was successfully set, but the Dock continues showing the old icon.
* **Cause**: macOS aggressively caches icons in Dock and Finder icon services.
* **Fix**:
  1. Touch the application bundle to update its modification time:
     ```bash
     touch "/Applications/<App>.app"
     ```
  2. Restart the Dock:
     ```bash
     killall Dock
     ```
  3. If still cached, clear icon service caches:
     ```bash
     sudo rm -rf /Library/Caches/com.apple.iconservices.store
     sudo find /private/var/folders/ -name com.apple.dock.iconcache -exec rm -rf {} \; || true
     killall Dock
     ```

## 4. Built-in Apple System Apps (App Store, Safari, Settings)

* **Symptom**: Cannot set custom icon on `/System/Applications/App Store.app`.
* **Cause**: macOS System Integrity Protection (SIP) and Signed System Volume (SSV). `/System/Applications` is mounted on a cryptographically sealed, read-only APFS snapshot.
* **Fix**: Create an AppleScript wrapper application in `/Applications` (e.g. `App Store Launcher.app` with `tell application "App Store" to activate`), assign the custom icon to that wrapper, and pin it to the Dock.
