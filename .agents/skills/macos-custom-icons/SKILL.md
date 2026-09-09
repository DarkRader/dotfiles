---
name: macos-custom-icons
description: >-
  Generate, customize, and declaratively configure custom macOS application icons (.icns)
  using the modern Apple continuous-curvature squircle style and integrate them with nix-darwin.
  Use when the user asks to create, customize, fix, or configure custom app icons on macOS.
---

# macOS Custom App Icons Skill

This skill provides procedures, automation scripts, and templates for designing, generating, and declaratively managing custom macOS application icons (`.icns`) with `nix-darwin`.

---

## Capabilities & Workflows

1. **Generate Custom Icons**: Create high-resolution multi-resolution `.icns` packages (16x16 to 1024x1024) matching Apple's Human Interface Guidelines squircle design (light/dark background, charcoal/monochrome symbol, transparent outer borders).
2. **Apply Safely**: Set custom icons using macOS native Cocoa `NSWorkspace.setIcon` without breaking Apple code signatures or Gatekeeper checks.
3. **Declare in Nix**: Add custom icons declaratively to `nix/shared.nix` or `nix/personal/default.nix` via `nix-darwin-custom-icons`.

---

## Directory Structure

* [`scripts/icon_tool.py`](./scripts/icon_tool.py): Comprehensive Python CLI tool to generate, style, and apply icons with custom background colors/gradients, icon colors, scaling, and auto-fetching from Simple Icons.
* [`scripts/generate-icon.sh`](./scripts/generate-icon.sh): Shell wrapper for icon generation.
* [`scripts/apply-icon.sh`](./scripts/apply-icon.sh): Script to safely apply an `.icns` file to any `.app` bundle via Cocoa `NSWorkspace`.
* [`resources/base-squircle.svg`](./resources/base-squircle.svg): Base SVG template of the Apple squircle tile.
* [`references/nix-darwin-integration.md`](./references/nix-darwin-integration.md): Guide for `nix-darwin-custom-icons` integration in flakes.
* [`references/troubleshooting.md`](./references/troubleshooting.md): Solutions for white dock borders, permission errors, and dock cache refresh.

---

## CLI Usage (`icon_tool.py`)

Run directly from your terminal:

```bash
.agents/skills/macos-custom-icons/scripts/icon_tool.py [options]
```

### CLI Options

| Flag | Description | Default | Example |
| :--- | :--- | :--- | :--- |
| `-q, --query` | Search term or link from Simple Icons / CDN | — | `--query slack` or `--query "https://simpleicons.org/?q=warp"` |
| `-a, --apply` | Target `.app` to immediately apply icon to & restart Dock | — | `--apply "/Applications/Slack.app"` |
| `-b, --bg` | Background color/gradient (`white`, `dark`, `slate`, or hex) | `white` | `--bg white` or `--bg "#FFFFFF,#EBECEF"` |
| `-c, --color` | Symbol color (`black`, `white`, `blue`, or hex) | `black` | `--color black` or `--color "#202022"` |
| `--shadow` / `--no-shadow` | Enable or disable smooth elevation shadow on symbol | `--shadow` | `--no-shadow` (for flat look) |
| `--scale` | Symbol scale factor (tuned for squircle grid) | `1.25` | `--scale 1.25` or `--scale 1.35` |
| `-o, --out` | Destination path for `.icns` | Auto-derived | `--out nix/icons/light/slack.icns` |
| `--preview` | Output a 1024x1024 PNG preview | Optional | `--preview` or `--preview /tmp/test.png` |
| `-l, --letter` | Generate an Apple-style monogram | — | `--letter "S"` or `--letter "AI"` |
| `--fallback-letter` | Fall back to an Apple lettermark if not found online | `false` | `--query myapp --fallback-letter` |
| `-s, --svg` | Local SVG file path | — | `--svg ./logo.svg` |
| `-p, --path` | Direct SVG path `d="..."` | — | `--path "M12 0C..."` |
| `-t, --theme` | Base theme preset (`light`, `dark`, `white`, `black`, `slate`) | `light` | `--theme dark` |
| `--no-dock-restart` | Do not restart Dock after applying icon | `false` | `--no-dock-restart` |

---

## Examples

### 1. Auto-Fetch & Apply with Custom Colors (One Command)
```bash
.agents/skills/macos-custom-icons/scripts/icon_tool.py \
  --query googlegemini \
  --bg "#FFFFFF,#EBECEF" \
  --color "#202022" \
  --scale 1.35 \
  --out nix/icons/light/gemini.icns \
  --apply "/Applications/Gemini.app"
```

### 2. Custom Colored Accent Icon (e.g. Blue Symbol on Slate Background)
```bash
.agents/skills/macos-custom-icons/scripts/icon_tool.py \
  --query discord \
  --bg "#F8FAFC,#E2E8F0" \
  --color "#5865F2" \
  --out nix/icons/light/discord.icns
```

### 3. Dark Theme Icon
```bash
.agents/skills/macos-custom-icons/scripts/icon_tool.py \
  --query obsidian \
  --theme dark \
  --color "#FFFFFF" \
  --out nix/icons/dark/obsidian.icns
```

### 4. From Local SVG File
```bash
.agents/skills/macos-custom-icons/scripts/icon_tool.py \
  --svg ./custom-logo.svg \
  --bg "#FFFFFF,#F3F4F6" \
  --color "#000000" \
  --out nix/icons/light/custom.icns
```

---

### 2. Adding to Nix Configuration

Add the icon mapping in `nix/shared.nix` (or host-specific `nix/personal/default.nix`):

```nix
environment.customIcons = {
  enable = true;
  icons = [
    {
      path = "/Applications/<App>.app";
      icon = ./icons/light/<app-name>.icns;
    }
  ];
};
```

Track and rebuild:
```bash
git add ~/dotfiles/nix/icons/light/<app-name>.icns
darwin-rebuild switch --flake ~/dotfiles/nix#macbook-personal
```

---

### 3. Immediately Applying to Running System

To apply the icon without waiting for a full system rebuild:

```bash
.agents/skills/macos-custom-icons/scripts/apply-icon.sh \
  "/Applications/<App>.app" \
  "$HOME/dotfiles/nix/icons/light/<app-name>.icns"
```

*Note: If the application in `/Applications` was installed with root privileges, prefix with `sudo`.*

---

## Important Rules

1. **Never write inside `/Applications/<App>.app/Contents/Resources/` directly**: Modifying files inside the app bundle breaks its code signature. Always use `NSWorkspace.setIcon` (which writes to `Icon\r` and sets extended attributes).
2. **Always ensure transparent corners**: When rendering SVGs, QuickLook may fill the outside with white. Always mask the outer area to alpha 0 before passing to `iconutil`.
3. **Stage new icon files in Git**: Nix flakes will ignore untracked binary files. Always run `git add nix/icons/light/<icon>.icns` so `darwin-rebuild` can evaluate them.
