# DarkRader Dotfiles

A centralized repository for managing system configurations and application settings on macOS using **GNU Stow**. 

By using Stow, all configurations are safely kept inside this single Git-tracked directory, while symlinks inside the home directory (`~/`) point directly here.

---

## ⚙️ Core Stow Concepts

* **Modifying an existing file:** Do nothing. Because the file in your home directory is already a symlink pointing here, changes you save are instantly applied.
* **Adding a brand new file:** You must explicitly run/refresh Stow so it creates the new symlink.

---

## 🚀 Useful Stow Commands

Always run these commands from the root of the `~/dotfiles` directory.

### Deploying Configs
Stow links files to the parent directory (`../`) by default. If a folder matches your home folder name directly (like `.config`), use standard stow:

```bash
# Link or update a package (e.g., .config or .warp)
stow -v .config

# Restow (re-calculate and fix symlinks for a package)
stow -Rv .config
```

#### The Target Flag Case (`-t`)
For root-level application folders where you want to keep the folder intact in this repo but only symlink the files inside it (like `.gemini`), use the target flag:

```bash
# Explicitly target a specific subfolder in your home directory
stow -v -t ~/.gemini .gemini

# Restow a target-based package
stow -Rv -t ~/.gemini .gemini
```

### Removing Configs
If you want to safely remove the symlinks from your home directory without deleting the actual configuration files from this repository:

```bash
# Remove symlinks for a normal package
stow -Dv .config

# Remove symlinks for a target-bound package
stow -Dv -t ~/.gemini .gemini
```

---

## 🛠️ Typical Use Cases

### Case A: You added a new tool configuration to `.config/`
1. Create the new application folder inside `./.config/` (e.g., `.config/new-app/config.toml`).
2. Refresh the `.config` package link:
   ```bash
   stow -Rv .config
   ```

### Case B: You want to update your `.gemini/settings.json`
1. Make your changes directly to `./.gemini/settings.json` inside this repository.
2. Save the file. The changes are immediately live because the home file is a symlink. No commands required!

---

## 🔍 Verifying Links
To verify that your file system is correctly linking back to this repository, check the file attributes:

```bash
ls -l ~/.gemini/settings.json
```

Expected output should show the symlink arrow:
```text
settings.json -> ../dotfiles/.gemini/settings.json
```

## Homebrew profiles

Homebrew dependencies are split into three manifests under `brewfiles/`:

* `brewfiles/.brewfile` contains shared dependencies and is the default.
* `brewfiles/.brewfile.personal` contains personal-only dependencies.
* `brewfiles/.brewfile.work` contains work-only dependencies.

After `brew install`, `brew uninstall`, `brew tap`, or `brew untap`, the wrapper asks which manifest to update. Press Enter to use the shared manifest. It records only the package named in that command, so unrelated installed packages are not copied into the selected profile.

To avoid the prompt for the current shell:

```bash
brew profile personal
brew profile work
brew profile shared
brew profile clear
```

Install the shared dependencies first, then the relevant overlay:

```bash
brew bundle --file=~/.brewfiles/.brewfile
brew bundle --file=~/.brewfiles/.brewfile.work
```

Keep shared dependencies only in `brewfiles/.brewfile`; keep context-specific dependencies in the corresponding overlay.

After adding the directory for the first time, refresh the root Stow package so it is available as `~/.brewfiles/`:

```bash
stow -Rv .
```
