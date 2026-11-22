# Global agent instructions (shared by Claude Code and opencode)

## Environment
- Shell is fish on macOS (Apple Silicon). Write fish-compatible commands for interactive use; use bash for scripts (`#!/usr/bin/env bash`).
- Dotfiles live in `~/dotfiles` and are symlinked into place by `install.py`. Edit the repo copy, never the symlink target elsewhere.
- Tool versions come from mise; Homebrew packages from `~/dotfiles/Brewfile`.

## Languages and tools
- **Python:** uv for everything (`uv run`, `uv add`, `uv sync`), ruff for lint and format, ty for type checking. Never use pip or poetry directly.
- **TypeScript/React:** bun for install and scripts, TSX, oxlint (type-aware) and oxfmt, `tsc --noEmit` for types. Match the repo's `check` script. Node version comes from `.node-version`.
- **Rust:** cargo with clippy, rustfmt, nextest when available. rustup owns the toolchain.
- **Task running:** prefer a repo's `justfile` or package scripts over ad-hoc commands.

## Secrets
- Project secrets (xray-atlas only) live in Infisical: run commands that need them via `infisical run --env=<env> -- <cmd>`.
- Personal secrets and tokens live in the macOS login Keychain (service `dotfiles:NAME`), loaded into env by `fish/secrets.fish`. This Mac is the source of truth. Never run `security find-generic-password`, `secret get`, or dump the keychain. Do not move them to Infisical.
- Never read, print, or commit `.env*` files, tokens, or `~/dotfiles/fish/env.local.fish`. Do not run `infisical export` or `infisical secrets`.

## Git
- Commits are SSH-signed. Never push, force-push, or rewrite published history unless asked.
- Follow each repo's own `AGENTS.md` for commit-message and co-author rules; it overrides defaults here.

## Working style
- Verify before claiming done: run the project's check/test command and report real output.
- Keep changes minimal and in the style of the surrounding code. Ask before deleting files you did not create.
