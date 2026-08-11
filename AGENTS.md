# AGENTS.md

## Repository Overview

This is a macOS dotfiles repository managed with GNU Stow. It contains shell,
terminal, editor, CLI, Raycast, and Homebrew configuration. There is no
application build system, runtime package, or automated test suite.

The repository is the source of truth. Stow creates symlinks in the user's
home directory; generated home-directory links must not be committed here.

## Important Paths

- `.config/`, `.gemini/`, `.warp/`, `.zsh/`: configuration packages.
- `.zshrc`: root-level shell entrypoint.
- `brewfiles/`: shared, personal, and work Homebrew manifests; applied
  manually, not Stow-managed.
- `raycast/`: Raycast import source; not Stow-managed.
- `.stowrc`: repository-wide Stow ignore rules.
- `.gitignore`: files excluded from Git.

`brewfiles/` and `raycast/` are intentionally ignored by `.stowrc` even though
their source files remain tracked by Git.

## Setup And Verification

From the repository root:

```bash
stow -nRv .  # preview changes
stow -Rv .   # create or repair symlinks
```

Use `stow -Dv .` to remove links without deleting repository files. Verify
links with `ls -l <home-path>` and `readlink <home-path>`.

Before claiming a documentation or configuration change is complete:

```bash
git diff --check
git status --short
```

There are no project tests to run. When Stow behavior is relevant, use its
simulation mode (`-n`) first and report any target conflicts.

## Change Workflow

1. Read the relevant package and existing documentation before editing.
2. Add or edit the source file inside this repository, not the generated file
   in `$HOME`.
3. Preview and restow with GNU Stow.
4. Confirm the expected home path is a symlink into this repository.
5. Keep unrelated working-tree changes intact and review `git diff`.

For a new home path, preserve its home-relative layout under the appropriate
package. For example, `~/.config/example/settings.toml` belongs at
`.config/example/settings.toml`.

## Safety And Style

- Do not commit secrets, tokens, private keys, machine-local state, or
  generated metadata.
- Prefer ASCII and concise Markdown.
- Keep documentation commands accurate for macOS and GNU Stow 2.x.
- Do not overwrite an unmanaged home file to resolve a Stow conflict; back it
  up or merge it deliberately.
- Keep changes focused. Do not reformat unrelated configuration or remove
  user changes already present in the working tree.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) so commit
types communicate semantic-versioning intent:

```text
<type>(<scope>): <short imperative description>
```

Use a relevant type such as `feat`, `fix`, `docs`, `chore`, `refactor`, or
`test`, and keep the scope specific, such as `stow`, `brewfiles`, `raycast`,
or `docs`. Mark breaking changes with `!` after the type or scope and explain
the impact in the commit body or footer.

After finishing a change, suggest the most relevant scoped commit message to
the user. Do not create a commit unless the user explicitly asks for one.
