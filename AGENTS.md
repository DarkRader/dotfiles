# AGENTS.md

## Repository Overview

This is a macOS dotfiles repository managed with [mise](https://mise.jdx.dev/). It contains shell,
terminal, editor, CLI, Raycast, and Homebrew configuration. There is no
application build system, runtime package, or automated test suite.

The repository is the source of truth. mise creates declarative symlinks in the user's
home directory; generated home-directory links must not be committed here.

## Important Paths

- `.config/`, `.warp/`, `.zsh/`: configuration packages.
- `.zshrc`: root-level shell entrypoint.
- `mise.toml`: declarative dotfile mappings and repository tasks.
- `brewfiles/`: shared, personal, and work Homebrew manifests; applied
  manually, not mise-managed.
- `nix/`: nix-darwin and Nix flake configuration; not mise-managed.
- `raycast/`: Raycast import source; not mise-managed.
- `.gitignore`: files excluded from Git.

`brewfiles/`, `nix/`, and `raycast/` are intentionally excluded from `mise.toml` even though
their source files remain tracked by Git.

## Setup And Verification

From the repository root:

```bash
mise dot diff    # preview changes (dry run)
mise dot apply   # create or repair symlinks
mise dot status  # inspect status of managed links
```

Use `mise dot unapply` to remove links without deleting repository files. Verify
links with `ls -l <home-path>` and `readlink <home-path>`.

Before claiming a documentation or configuration change is complete:

```bash
git diff --check
git status --short
```

There are no project tests to run. When dotfile behavior is relevant, use
`mise dot diff` first and report any target conflicts.

## Change Workflow

1. Read the relevant package and existing documentation before editing.
2. Add or edit the source file inside this repository, not the generated file
   in `$HOME`.
3. For a new path, declare it in `mise.toml` under `[dotfiles]` (or run `mise dot add -l <path>`).
4. Preview with `mise dot diff` and apply with `mise dot apply`.
5. Confirm the expected home path is a symlink into this repository.
6. Keep unrelated working-tree changes intact and review `git diff`.

For a new home path, preserve its home-relative layout under the appropriate
package. For example, `~/.config/example/settings.toml` belongs at
`.config/example/settings.toml`.

## Safety And Style

- Do not commit secrets, tokens, private keys, machine-local state, or
  generated metadata.
- Prefer ASCII and concise Markdown.
- Keep documentation commands accurate for macOS and mise.
- Do not overwrite an unmanaged home file to resolve a conflict; back it
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
`test`, and keep the scope specific, such as `mise`, `nix`, `brewfiles`, `raycast`,
or `docs`. Mark breaking changes with `!` after the type or scope and explain
the impact in the commit body or footer.

After finishing a change, suggest the most relevant scoped commit message to
the user. Do not create a commit unless the user explicitly asks for one.
