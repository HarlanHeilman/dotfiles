set shell := ["bash", "-cu"]

# List recipes
default:
    @just --list

# Preview what install.py would change
dry:
    uv run install.py --dry-run

# Apply dotfile symlinks and configs
install:
    uv run install.py

# Install everything in the Brewfile
bundle:
    brew bundle --file=Brewfile

# Show packages missing from the Brewfile (what's installed but untracked)
drift:
    brew bundle cleanup --file=Brewfile

# Update every toolchain
update:
    brew update && brew upgrade
    mise up
    rustup update
    uv self update
    bun upgrade

# Check fish config parses and tools resolve
doctor:
    fish -n fish/config.fish
    fish -ic 'for t in zoxide atuin mise delta starship fzf just ruff ty node; type -q $t; or echo "missing: $t"; end'
