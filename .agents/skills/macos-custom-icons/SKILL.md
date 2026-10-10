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

* [`resources/base-squircle.svg`](./resources/base-squircle.svg): Base SVG template of the Apple squircle tile.
* [`references/nix-darwin-integration.md`](./references/nix-darwin-integration.md): Guide for `nix-darwin-custom-icons` integration in flakes.
* [`references/troubleshooting.md`](./references/troubleshooting.md): Solutions for white dock borders, permission errors, and dock cache refresh.

---

## CLI Tooling (`macicon`)

The custom icon generation and application engine is powered directly by the standalone `macicon` CLI tool ([DarkRader/macicon](https://github.com/DarkRader/macicon)), managed repo-locally via `mise` in `mise.toml` (`"github:DarkRader/macicon" = "0.3.0"`).

All icon generation, theme synchronization, and application workflows are invoked via `mise run icon <flags>` or `mise exec -- macicon <flags>`. Dedicated task shortcuts (`icon:sync`, `icon:all`, `icon:create-theme`, `icon:preview`) are also available in `mise.toml`.

### CLI Options

| Flag | Description | Default | Example |
| :--- | :--- | :--- | :--- |
| `--create-theme` | Batch generate all existing icons into a new theme folder | — | `mise run icon:create-theme nord --bg "#2E3440" --color "#ECEFF4"` |
| `--all-themes` | Generate icon across all registered themes in `themes.json` | `false` | `mise run icon:all linear` |
| `--sync-themes` | Ensure all themes have the complete set of icons | `false` | `mise run icon:sync` |
| `-q, --search-query` | Search term or link from Simple Icons / CDN | — | `mise run icon -q slack` or `mise run icon slack` |
| `--icns` | Path to an existing `.icns` file to apply or preview | — | `mise run icon --icns nix/icons/light/slack.icns --apply "/Applications/Slack.app"` |
| `-a, --apply` | Target `.app` to immediately apply icon to & restart Dock | — | `mise run icon slack --apply "/Applications/Slack.app"` |
| `-b, --bg` | Background color/gradient (`white`, `dark`, `slate`, `nord`, or hex) | `white` | `--bg white` or `--bg "#FFFFFF,#EBECEF"` |
| `-c, --color` | Symbol color (`black`, `white`, `blue`, or hex) | `black` | `--color black` or `--color "#202022"` |
| `--shadow` / `--no-shadow` | Enable or disable smooth elevation shadow on symbol | `--shadow` | `--no-shadow` (for flat look) |
| `--scale` | Symbol scale factor (tuned for squircle grid) | `1.25` | `--scale 1.25` or `--scale 1.35` |
| `-o, --out` | Destination path for `.icns` | Auto-derived | `--out nix/icons/light/slack.icns` |
| `--from-theme` | Reference theme to discover icons from (with `--create-theme`) | `light` | `--from-theme dark` |
| `--preview` | Output a 1024x1024 PNG preview | Optional | `--preview` or `mise run icon:preview slack` |
| `-l, --letter` | Generate an Apple-style monogram | — | `--letter "S"` or `--letter "AI"` |
| `--fallback-letter` | Fall back to an Apple lettermark if not found online | `false` | `mise run icon myapp --fallback-letter` |
| `-s, --svg` | Local SVG file path | — | `--svg ./logo.svg` |
| `-p, --path` | Direct SVG path `d="..."` | — | `--path "M12 0C..."` |
| `-t, --theme` | Base preset (`light`, `dark`, `white`, `black`, `slate`, `nord`, `catppuccin`, `dracula`) | `light` | `--theme nord` |
| `--no-dock-restart` | Do not restart Dock after applying icon | `false` | `--no-dock-restart` |

---

## Examples

### 1. Batch Create a New Theme Folder (All Existing Icons)
Generate a full set of icons for a new theme (e.g. `nord`, `catppuccin`, or custom colors) in a single command:
```bash
mise run icon:create-theme nord \
  --bg "#2E3440" \
  --color "#ECEFF4" \
  --no-shadow
```
*Discovers all existing icons in `nix/icons/light/` and generates matching `.icns` files in `nix/icons/nord/`, registering the theme in `nix/icons/themes.json`.*

### 2. Add a New App Icon Across All Existing Themes
When adding a newly installed app to your configuration, generate its icon for all registered themes at once:
```bash
mise run icon:all raycast
# or:
mise run icon raycast --all-themes
```
*Generates `raycast.icns` in `nix/icons/light/`, `nix/icons/dark/`, and any other theme folders configured in `themes.json`.*

### 3. Auto-Fetch & Apply with Custom Colors (Single Icon)
```bash
mise run icon googlegemini \
  --bg "#FFFFFF,#EBECEF" \
  --color "#202022" \
  --scale 1.35 \
  --out nix/icons/light/gemini.icns \
  --apply "/Applications/Gemini.app"
```

### 4. Custom Colored Accent Icon
```bash
mise run icon discord \
  --bg "#F8FAFC,#E2E8F0" \
  --color "#5865F2" \
  --out nix/icons/light/discord.icns
```

### 5. Dark Theme Icon
```bash
mise run icon obsidian \
  --theme dark \
  --color "#FFFFFF" \
  --out nix/icons/dark/obsidian.icns
```

### 6. From Local SVG File
```bash
mise run icon \
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

To apply an existing icon without waiting for a full system rebuild:

```bash
mise run icon \
  --icns "$HOME/dotfiles/nix/icons/light/<app-name>.icns" \
  --apply "/Applications/<App>.app"
```

*Note: If the application in `/Applications` was installed with root privileges, prefix with `sudo`: `sudo mise exec -- macicon --icns ... --apply ...`.*

---

## Important Rules

1. **Never write inside `/Applications/<App>.app/Contents/Resources/` directly**: Modifying files inside the app bundle breaks its code signature. Always use `NSWorkspace.setIcon` (which writes to `Icon\r` and sets extended attributes).
2. **Always ensure transparent corners**: When rendering SVGs, QuickLook may fill the outside with white. Always mask the outer area to alpha 0 before passing to `iconutil`.
3. **Stage new icon files in Git**: Nix flakes will ignore untracked binary files. Always run `git add nix/icons/light/<icon>.icns` so `darwin-rebuild` can evaluate them.
