# Nix-Darwin Configuration

Declarative macOS system configuration using Nix Flakes, [nix-darwin](https://github.com/nix-darwin/nix-darwin), and [nix-homebrew](https://github.com/zhaofengli/nix-homebrew).

This directory manages system packages, macOS defaults, and Homebrew casks and formulae declaratively.

## Profiles

| Profile | Target User | Configuration |
| --- | --- | --- |
| `macbook-personal` | `Artyom` | [personal/default.nix](personal/default.nix) + [shared.nix](shared.nix) |
| `macbook-work` | `artemk` | [work/default.nix](work/default.nix) + [shared.nix](shared.nix) |

## Initial Setup On A New Mac

### 1. Install Command Line Tools & Nix

Install Apple Command Line Tools (provides `git` and core developer tools):

```bash
xcode-select --install
```

Install Nix using the Determinate Systems installer:

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

Restart your terminal or open a new shell session so the `nix` command is in your `PATH`.

### 2. Bootstrap nix-darwin

Run the initial `darwin-rebuild` command for your profile:

For personal:

```bash
nix run nix-darwin/master#darwin-rebuild -- switch --flake ~/dotfiles/nix#macbook-personal
```

For work:

```bash
nix run nix-darwin/master#darwin-rebuild -- switch --flake ~/dotfiles/nix#macbook-work
```

---

## Daily Workflow & Commands

Once nix-darwin is activated, `darwin-rebuild` is available directly in your shell:

### Applying Changes

After modifying any `.nix` files:

```bash
# Personal profile
darwin-rebuild switch --flake ~/dotfiles/nix#macbook-personal

# Work profile
darwin-rebuild switch --flake ~/dotfiles/nix#macbook-work
```

### Checking Configuration

Verify flake evaluation and build without activating changes:

```bash
darwin-rebuild check --flake ~/dotfiles/nix#macbook-personal
```

### Updating Flake Dependencies

Update input locks in `flake.lock` (`nixpkgs`, `nix-darwin`, `nix-homebrew`):

```bash
cd ~/dotfiles/nix
nix flake update
darwin-rebuild switch --flake ~/dotfiles/nix#macbook-personal
```

### Garbage Collection

Clean up old generations and unused Nix store paths:

```bash
nix-collect-garbage -d
```

---

## Directory Structure

- `flake.nix`: Flake entrypoint configuring inputs and mapping profiles (`macbook-personal`, `macbook-work`) to primary users.
- `shared.nix`: Top-level shared configuration aggregating modular components.
- `modules/`:
  - `theme.nix`: Visual theming (icon theme, wallpaper management, and activation).
  - `wrappers.nix`: System application wrappers (`~/Applications`) for protected macOS apps.
  - `icons.nix`: Custom application icon mappings.
  - `defaults.nix`: macOS system preferences (Dock, Finder, Trackpad, Dark mode, Siri).
  - `homebrew.nix`: Homebrew formulae and desktop application casks.
  - `packages.nix`: Common CLI and development packages.
- `personal/`: Personal profile overlay.
  - `default.nix`: Imports personal submodules.
  - `dock.nix`: Personal Dock persistent-apps.
  - `homebrew.nix`: Personal Homebrew formulae, casks, and App Store apps.
  - `packages.nix`: Personal system packages.
  - `theme.nix`: Personal wallpaper and icon theme selection.
  - `icons.nix`: Personal custom application icons.
- `work/`: Work profile overlay.
  - `default.nix`: Imports work submodules.
  - `dock.nix`: Work Dock persistent-apps.
  - `homebrew.nix`: Work Homebrew formulae and casks.
