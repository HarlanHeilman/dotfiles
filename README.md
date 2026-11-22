# Dotfiles

Fish-first macOS (and Linux) setup for Python (uv, ruff, ty), Rust, and TypeScript (bun, oxlint, oxfmt), with shared Claude Code and opencode agent config.

## Layout

| Path | What it configures |
| --- | --- |
| `fish/` | Config, env, aliases, functions (`cd` via zoxide, `mkcd`, `y`, auth helpers) |
| `starship/` | Prompt (ANSI colors, follows the terminal theme) |
| `ghostty/`, `kitty/` | Terminals: macOS system colors, Liquid Glass (Ghostty), light/dark auto |
| `atuin/`, `mise/`, `ruff/`, `cargo/`, `uv/`, `lazygit/` | Tool configs |
| `git/` | Shared git settings and delta, included from `~/.gitconfig` |
| `zed/` | Zed settings, keymap, snippets |
| `claude/` | `settings.json` (permissions, deny rules, format hook) |
| `agents/` | `AGENTS.md` shared by Claude Code and opencode, opencode config, custom skills |
| `ssh/`, `launchd/`, `bin/` | SSH policy, LaunchAgents, helper scripts |
| `Brewfile`, `justfile`, `install.py` | Packages, task runner, symlink installer |

## Setup

```bash
git clone <repo> ~/dotfiles && cd ~/dotfiles
brew bundle            # packages (or: just bundle)
uv run install.py      # symlinks + configs (preview with --dry-run)
chsh -s /opt/homebrew/bin/fish
```

Optional: `bin/macos-defaults` applies keyboard, Finder, Dock and screenshot preferences. Review it first.

## Daily commands

`just` lists recipes: `dry`, `install`, `bundle`, `drift`, `update`, `doctor`.

## Local secrets

Personal tokens live in the macOS login Keychain, not in files: `secret set NAME`, `secret list` (names are listed in `fish/secrets.fish` and exported at shell start). Non-secret machine overrides go in gitignored `fish/env.local.fish` (copy from `env.local.example.fish`) or `~/.config/fish/config.local.fish`. This Mac is the source of truth for personal secrets. Infisical is used only for the xray-atlas project (`infisical run -- ...`); agents are denied access to `.env*` and these files.

## Notes

- `cd` is a fish function (`fish/functions/cd.fish`): flags and no-arg use the builtin, everything else goes through zoxide. `cdi` is the interactive picker.
- Tool versions come from mise (`mise/config.toml`, plus per-project `.node-version`).
- Needs a Nerd Font only as a symbol fallback; text uses SF Mono.
