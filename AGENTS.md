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
- `mise.toml`: declarative dotfile mappings, tool definitions, and repository tasks.
- `nix/`: nix-darwin and Nix flake configuration (including declarative
  Homebrew via nix-homebrew); operated via repository `mise` tasks (`nix:*`),
  excluded from `[dotfiles]` symlinks.
- `raycast/`: Raycast import source; not mise-managed.
- `.gitignore`: files excluded from Git.

`nix/` and `raycast/` are intentionally excluded from `[dotfiles]` in `mise.toml`
even though their source files remain tracked by Git.

## Setup And Verification

From the repository root:

```bash
mise dot diff    # preview changes (dry run)
mise dot apply   # create or repair symlinks
mise dot status  # inspect status of managed links
```

Use `mise dot unapply` to remove links without deleting repository files. Verify
links with `ls -l <home-path>` and `readlink <home-path>`.

### Repository Tasks

Task suites are configured in `mise.toml` (`mise tasks`):

- **Verification**: `mise check` (runs `dot:diff`, `nix:check`, and `git diff --check` in one step)
- **Dotfiles**: `mise dot:apply`, `mise dot:diff`, `mise dot:status`, `mise dot:add <path>`, `mise dot:unapply`
- **Nix-Darwin**: `mise nix:personal` (alias `darwin:personal`), `mise nix:work` (alias `darwin:work`), `mise nix:check` (alias `darwin:check`), `mise nix:build`, `mise nix:update`, `mise nix:gc`
- **Icons (`macicon`)**: `mise icon`, `mise icon:sync`, `mise icon:all`, `mise icon:create-theme`, `mise icon:preview`

Before claiming a documentation or configuration change is complete:

```bash
mise check
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
`test`, and keep the scope specific, such as `mise`, `nix`, `raycast`,
or `docs`. Mark breaking changes with `!` after the type or scope and explain
the impact in the commit body or footer.

After finishing a change, suggest the most relevant scoped commit message to
the user. Do not create a commit unless the user explicitly asks for one.
