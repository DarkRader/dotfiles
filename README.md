# DarkRader Dotfiles

This repository is the source of truth for macOS shell, terminal, editor, and
application configuration. It uses [mise](https://mise.jdx.dev/) to expose the
files in this repository through declarative symlinks in `$HOME`.

## How It Works

- Git tracks the real configuration files in this repository.
- `mise` creates declarative symlinks in your home directory pointing back here.
- Edit a tracked file in this repository; the linked application sees the
  change immediately.
- Do not commit symlinks from your home directory. Symlinks are generated
  by `mise` and belong outside the repository.

Managed configurations include `.config/` (GitHub CLI, OpenLogi, Starship, Zed),
`.warp/` settings and themes, `.zsh/`, and root-level files such as `.zshrc`.
`brewfiles/`, `nix/`, and `raycast/` remain versioned in Git but are intentionally
excluded from `[dotfiles]` in `mise.toml`: Nix is managed declaratively via
nix-darwin and repository `mise` tasks, Homebrew is declarative via
nix-homebrew, and Raycast is imported through its application UI.

## First Setup On A New Mac

To bootstrap a new Mac with Nix, [nix-darwin](https://github.com/nix-darwin/nix-darwin), and [nix-homebrew](https://github.com/zhaofengli/nix-homebrew):

```bash
# 1. Install Apple Command Line Tools (provides git and core build tools)
xcode-select --install

# 2. Install Nix (Determinate Systems installer)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# 3. Clone the repository
git clone https://github.com/DarkRader/dotfiles ~/dotfiles
cd ~/dotfiles

# 4. Bootstrap nix-darwin (choose personal or work profile)
nix run nix-darwin/master#darwin-rebuild -- switch --flake ~/dotfiles/nix#macbook-personal
# or for work:
# nix run nix-darwin/master#darwin-rebuild -- switch --flake ~/dotfiles/nix#macbook-work

# 5. Link dotfiles with mise
mise dot apply
```

See [nix/README.md](nix/README.md) for full documentation, profile differences, and daily commands.

If `mise dot apply` reports a conflict, inspect the existing file first. Move or remove an
old, unmanaged configuration only after deciding whether it should be kept.

After setup, verify links with `mise dot status`:

```bash
mise dot status
```

Or inspect individual symlinks:

```bash
ls -l ~/.zshrc
readlink ~/.zshrc
ls -ld ~/.config/starship.toml
readlink ~/.config/starship.toml
```

Inspected paths should resolve into `~/dotfiles`. Start a new shell after linking
`.zshrc` so the shell loads the managed configuration.

## Updating Existing Configuration

Edit the source file under `~/dotfiles`. No `mise` command is needed when the
symlink already exists:

```bash
$EDITOR ~/dotfiles/.zshrc
$EDITOR ~/dotfiles/.config/starship.toml
```

If a new file was mapped in `mise.toml`, apply the updates:

```bash
cd ~/dotfiles
mise dot apply
```

Use `mise dot unapply` to remove managed symlinks from `$HOME`. This does not
delete the source files in the repository.

## Adding A New Managed File

You can add a new configuration file in two ways:

### Option A: Using the CLI (Recommended)

From within `~/dotfiles`, run:

```bash
mise dot add -l ~/.config/example/settings.toml
# or via mise task:
mise run dot:add ~/.config/example/settings.toml
```

This moves the file into `~/dotfiles/.config/example/settings.toml`, maps it in
`mise.toml`, and creates the symlink back to `$HOME`.

### Option B: Manual Mapping

1. Put the file in this repository, preserving the path it should have under `$HOME`.
2. Add the path under `[dotfiles]` in `mise.toml`:
   ```toml
   "~/.config/example/settings.toml" = {}
   ```
3. Preview the change with `mise dot diff`.
4. Apply with `mise dot apply`.
5. Review and commit the source file with Git.

## Repository Tasks (Mise)

The repository provides task suites configured in `mise.toml`. Inspect available tasks with `mise tasks`:

### Dotfiles Management

| Command | Purpose |
| --- | --- |
| `mise dot apply` / `mise run dot:apply` | Apply dotfile symlinks into `$HOME` |
| `mise dot diff` / `mise run dot:diff` | Preview dotfile changes (dry run) |
| `mise dot status` / `mise run dot:status` | Show status of managed dotfiles |
| `mise dot add -l <path>` / `mise run dot:add <path>` | Add and symlink a new dotfile into this repo |
| `mise dot unapply` / `mise run dot:unapply` | Remove managed symlinks from `$HOME` |

### Nix-Darwin & Flake Management

| Command | Purpose |
| --- | --- |
| `mise run nix:personal` *(alias: `darwin:personal`)* | Rebuild and apply personal macOS configuration |
| `mise run nix:work` *(alias: `darwin:work`)* | Rebuild and apply work macOS configuration |
| `mise run nix:check` *(alias: `darwin:check`)* | Verify flake evaluation without activating changes |
| `mise run nix:build` | Build personal system configuration without activating |
| `mise run nix:update` | Update `flake.lock` dependencies |
| `mise run nix:gc` | Clean up old generations and garbage collect Nix store |

### Custom Icons (`macicon`)

| Command | Purpose |
| --- | --- |
| `mise run icon` | Run the `macicon` CLI |
| `mise run icon:sync` | Regenerate missing icons across themes in `themes.json` |
| `mise run icon:all` | Generate an icon across all registered themes |
| `mise run icon:create-theme` | Batch generate existing icons into a new theme folder |
| `mise run icon:preview` | Generate an icon with a 1024x1024 PNG preview |

## Packages And Layout

| Path | Purpose |
| --- | --- |
| `.config/` | Application configurations (GitHub CLI, OpenLogi, Starship, Zed) |
| `.warp/` | Warp terminal settings and themes |
| `.zsh/` and `.zshrc` | Shell configuration and entrypoint |
| `mise.toml` | Declarative dotfile mappings, tool definitions, and repository tasks |
| `brewfiles/` | Homebrew manifests and instructions; applied manually or via nix-homebrew |
| `nix/` | nix-darwin and Nix flake system configuration; operated via `mise run nix:*` |
| `raycast/` | Raycast import source; not mise-managed |

Files such as `.DS_Store`, credentials, and machine-local state should not be added
to the repository. Extend `.gitignore` when a new non-configuration file should be
ignored by Git.

Nix and Homebrew configurations are documented separately in
[nix/README.md](nix/README.md) and [brewfiles/README.md](brewfiles/README.md).
