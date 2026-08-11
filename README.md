# DarkRader Dotfiles

This repository is the source of truth for macOS shell, terminal, editor, and
application configuration. It uses [GNU Stow](https://www.gnu.org/software/stow/)
to expose the files in this repository through symlinks in `$HOME`.

## How It Works

- Git tracks the real configuration files in this repository.
- GNU Stow creates symlinks in your home directory that point back here.
- Edit a tracked file in this repository; the linked application sees the
  change immediately.
- Do not commit symlinks from your home directory. The symlinks are generated
  by Stow and belong outside the repository.

The top-level package is intentionally used for the initial setup. It manages
directories such as `.config`, `.gemini`, `.warp`, and `.zsh`, plus root-level
files such as `.zshrc`. `brewfiles/` and `raycast/` remain versioned in Git but
are intentionally excluded from Stow: Homebrew is run manually and Raycast is
imported through its application UI. Depending on whether a
target directory already exists, Stow may create one directory symlink or
individual file symlinks inside that directory; both point back to the same
tracked source files.

If individual file symlinks are required for a package, use Stow's
`--no-folding` option, for example `stow -Rv --no-folding .config`. This is
optional; the default directory folding is safe and keeps the home directory
tidy.

## First Setup On A New Mac

Install Homebrew first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Git and Stow and clone the repository:

```bash
brew install git stow
git clone https://github.com/DarkRader/dotfiles ~/dotfiles
cd ~/dotfiles
```

Both `git` and `stow` are also recorded in the shared
`brewfiles/.brewfile`. The explicit install above bootstraps the tools needed
to clone and link this repository; after cloning, apply the full shared
profile with:

```bash
brew bundle --file=~/dotfiles/brewfiles/.brewfile
```

Preview the links before changing your home directory:

```bash
stow -nRv .
```

If the preview is correct, create the symlinks:

```bash
stow -Rv .
```

If Stow reports a conflict, inspect the existing file first. Move or remove an
old, unmanaged configuration only after deciding whether it should be kept;
Stow will not overwrite it automatically.

After setup, verify a link points into this repository. Depending on Stow's
directory-folding decision, inspect either the package directory or a file
inside it:

```bash
ls -l ~/.zshrc
readlink ~/.zshrc
ls -ld ~/.config ~/.config/starship.toml
readlink ~/.config
readlink ~/.config/starship.toml
```

At least the inspected path should resolve into `~/dotfiles`. Start a new
shell after linking `.zshrc` so the shell loads the managed configuration.

## Updating Existing Configuration

Edit the source file under `~/dotfiles`. No Stow command is needed when the
symlink already exists:

```bash
$EDITOR ~/dotfiles/.zshrc
$EDITOR ~/dotfiles/.config/starship.toml
```

If a directory or file was added, moved, or renamed, restow the package:

```bash
cd ~/dotfiles
stow -Rv .
```

Use `stow -Dv .` to remove this package's symlinks from `$HOME`. This does not
delete the source files in the repository.

## Adding A New Managed File

1. Put the file in the matching package in this repository, preserving the
   path it should have under `$HOME`.
2. Preview the change with `stow -nRv .`.
3. Restow with `stow -Rv .`.
4. Confirm the home-directory path is a symlink to the repository.
5. Review and commit the source file with Git.

For example, to manage `~/.config/example/settings.toml`:

```bash
mkdir -p ~/dotfiles/.config/example
$EDITOR ~/dotfiles/.config/example/settings.toml
cd ~/dotfiles
stow -nRv .
stow -Rv .
ls -l ~/.config/example/settings.toml
git add .config/example/settings.toml
```

If the target already exists as a regular file, back it up or merge its
contents before running Stow. Never copy a generated home-directory symlink
back into the repository as a new tracked file.

## Packages And Layout

| Path | Purpose |
| --- | --- |
| `.config/` | XDG application configuration |
| `.gemini/` | Gemini CLI configuration |
| `.warp/` | Warp terminal settings and themes |
| `.zsh/` and `.zshrc` | Shell configuration |
| `brewfiles/` | Homebrew manifests and instructions; applied manually |
| `raycast/` | Raycast import source; not Stow-managed |

The root `.stowrc` excludes repository metadata and documentation from Stow.
Files such as `.DS_Store`, editor metadata, credentials, and other machine-
local artifacts should not be added to the repository. Extend `.gitignore` and
`.stowrc` when a new non-configuration file should be ignored by Git or Stow.

Homebrew profiles are documented separately in
[brewfiles/README.md](brewfiles/README.md).
