# Homebrew Profiles

Homebrew dependencies are split into three manifests:

- `.brewfile` contains shared dependencies and is the default.
- `.brewfile.personal` contains personal-only dependencies.
- `.brewfile.work` contains work-only dependencies.

The shared manifest already includes the bootstrap tools `git` and `stow`.
Check whether they are installed and managed by Homebrew with:

```bash
brew list --versions git stow
which -a git stow
brew bundle check --file=~/dotfiles/brewfiles/.brewfile
```

`/usr/bin/git` is Apple's system Git and is not the same as the Homebrew
formula. If `brew list --versions` does not show a package, install it with
`brew install git` or `brew install stow`; no manual Brewfile migration is
needed because both entries are already tracked in `.brewfile`.

Install shared dependencies first, then the relevant overlay. Run these from
the repository root, or replace `~/dotfiles` with the actual clone path:

```bash
brew bundle --file=~/dotfiles/brewfiles/.brewfile
brew bundle --file=~/dotfiles/brewfiles/.brewfile.work
```

Use `.brewfile.personal` instead for a personal machine. The `brew` wrapper
updates the selected manifest after `brew install`, `brew uninstall`, `brew
tap`, or `brew untap`. It records only the package named in that command, so
unrelated installed packages are not copied into the profile.

To choose a profile without being prompted in the current shell:

```bash
brew profile personal
brew profile work
brew profile shared
brew profile clear
```

Keep dependencies used everywhere in `.brewfile`. Put context-specific tools
only in the matching personal or work overlay.

This directory is intentionally not Stow-managed. On a fresh machine, clone
the repository, run the setup in the root [README](../README.md), and then run
the commands above manually.
