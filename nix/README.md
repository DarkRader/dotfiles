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
- `shared.nix`: Common packages (Neovim, Git, Starship, tmux, Node, uv, etc.), macOS system defaults (Dark mode, Dock, Finder, Trackpad), and shared Homebrew formulae/casks.
- `personal/default.nix`: Personal overlay with personal packages, Dock layout, and casks (e.g., IINA).
- `work/default.nix`: Work overlay with work-specific packages and casks (e.g., Slack, Microsoft Teams, Azure CLI, Poetry).
