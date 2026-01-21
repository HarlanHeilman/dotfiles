# Dotfiles

Cross-platform shell configuration for macOS and Linux with a focus on Python, Rust, and web development workflows.

## Features

- **Cross-platform**: Automatic OS detection with platform-specific configurations
- **Shell support**: bash and zsh configurations
- **Starship prompt**: Fast, minimal prompt with Catppuccin Frappe theme
- **Modern CLI tools**: Configured for fzf, bat, eza, ripgrep, fd
- **Python workflow**: uv integration, virtualenv helpers, maturin support
- **Git shortcuts**: Quick commit, status, and log aliases

## Structure

```
dotfiles/
├── .bashrc              # Bash configuration
├── .zshrc               # Zsh configuration
├── .gitignore
├── install.py           # Installation script (run with uv)
├── README.md
├── catppuccin/
│   └── catppuccin_frappe.omp.json   # Oh-My-Posh theme (legacy)
├── fzf/
│   └── init.sh          # fzf configuration with Catppuccin colors
├── lazygit/
│   └── config.yml       # Lazygit configuration
├── nushell/             # Legacy Nushell configs (reference only)
├── starship/
│   └── starship.toml    # Starship prompt configuration
└── uv/
    └── uv.toml          # uv Python package manager settings
```

## Requirements

- Python 3.11+ (for installation script)
- [uv](https://github.com/astral-sh/uv) - Python package manager
- A [Nerd Font](https://www.nerdfonts.com/) installed and configured in your terminal

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/dotfiles.git ~/dotfiles
cd ~/dotfiles

# Preview what will be installed (dry run)
uv run install.py --dry-run

# Install dotfiles
uv run install.py

# Install with dependencies (starship, fzf, bat, etc.)
uv run install.py --install-deps
```

### Installation Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without modifying anything |
| `--no-backup` | Skip backing up existing configuration files |
| `--install-deps` | Install recommended CLI tools via Homebrew/apt |

### Tool Status Check

The installer automatically checks which tools are installed and provides:

- List of installed vs missing tools
- Required tools marked with `[*]`
- Platform-specific installation commands

Example output:

```
------------------------------------------------------------
  Tool Status
------------------------------------------------------------

  Installed:
    [*] Starship     - Cross-shell prompt
    [*] uv           - Python package manager
    [ ] fzf          - Fuzzy finder

  Missing:
    [ ] bat          - Cat replacement with syntax highlighting
    [ ] eza          - Modern ls replacement

  [*] = Required

------------------------------------------------------------
  Installation Commands
------------------------------------------------------------

  Recommended:
    brew install bat eza
```

### Manual Installation

If you prefer manual setup:

```bash
# Shell configs
ln -sf ~/dotfiles/.zshrc ~/.zshrc
ln -sf ~/dotfiles/.bashrc ~/.bashrc

# Starship
mkdir -p ~/.config
ln -sf ~/dotfiles/starship/starship.toml ~/.config/starship.toml

# Lazygit
mkdir -p ~/.config/lazygit
ln -sf ~/dotfiles/lazygit/config.yml ~/.config/lazygit/config.yml

# uv
mkdir -p ~/.config/uv
ln -sf ~/dotfiles/uv/uv.toml ~/.config/uv/uv.toml
```

## Dependencies

### Required

| Tool | Description | Install |
|------|-------------|---------|
| [starship](https://starship.rs/) | Cross-shell prompt | `brew install starship` |
| [uv](https://github.com/astral-sh/uv) | Python package manager | `brew install uv` |

### Recommended

| Tool | Purpose | Install |
|------|---------|---------|
| [fzf](https://github.com/junegunn/fzf) | Fuzzy finder | `brew install fzf` |
| [bat](https://github.com/sharkdp/bat) | Cat with syntax highlighting | `brew install bat` |
| [eza](https://github.com/eza-community/eza) | Tree view and extended listings | `brew install eza` |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | Fast grep | `brew install ripgrep` |
| [fd](https://github.com/sharkdp/fd) | Fast find | `brew install fd` |
| [lazygit](https://github.com/jesseduffield/lazygit) | Git TUI | `brew install lazygit` |
| [neovim](https://neovim.io/) | Text editor | `brew install neovim` |

### Install All (macOS)

```bash
brew install starship uv fzf bat eza ripgrep fd lazygit neovim
```

### Install All (Linux/Homebrew)

```bash
brew install starship uv fzf bat eza ripgrep fd lazygit neovim
```

### Install All (Linux/apt)

```bash
sudo apt install fzf bat ripgrep fd-find
# Starship requires manual installation
curl -sS https://starship.rs/install.sh | sh
```

## Shell Aliases

### Navigation

| Alias | Command |
|-------|---------|
| `dot` | `cd $DOTFILES` |
| `proj` | `cd $PROJECTS` |

### Git

| Alias | Command |
|-------|---------|
| `gc "message"` | `git add . && git commit -m "message" && git push` |
| `gs` | `git status` |
| `gd` | `git diff` |
| `gl` | `git log --oneline -n 20` |
| `gp` | `git pull` |

### Python

| Alias | Command |
|-------|---------|
| `py` | `python3` |
| `pip` | `uv pip` |
| `venv` | Create and activate `.venv` |
| `activate` | `source ./.venv/bin/activate` |
| `build` | `venv && maturin develop --uv` |

### Modern Tools (when installed)

| Alias | Command |
|-------|---------|
| `cat` | `bat --style=plain` |
| `tree` | `eza --tree --level=2 --icons` |
| `tree3` | `eza --tree --level=3 --icons` |
| `lx` | `eza -la --icons --git` (extended listing) |

Note: `ls`, `ll`, `la` use the system default for familiarity.

## Prompt

The Starship prompt displays:

```
[python] [rust] [node] @hostname ~/path/to/dir  branch status    duration
>
```

| Element | When Shown |
|---------|------------|
| Python version + venv | In Python projects |
| Rust version | In Rust projects |
| Node version | When package.json present |
| Hostname | Always |
| Directory | Always (truncated to 4 levels) |
| Git branch | In git repositories |
| Git status | When there are changes |
| Command duration | When command takes >500ms |

### Vi Mode

The prompt character changes based on vi mode:

| Mode | Symbol |
|------|--------|
| Insert | `>` (green) |
| Normal | `<` (purple) |
| Replace | `<` (peach) |
| Visual | `<` (yellow) |
| Error | `>` (red) |

## Theme

All configurations use the [Catppuccin Frappe](https://github.com/catppuccin/catppuccin) color palette.

## Platform Notes

### macOS

- Homebrew paths are automatically added (`/opt/homebrew/bin`)
- Uses `ls -G` for colored output (or eza if installed)
- Clipboard: `pbcopy`

### Linux

- Supports Intel oneAPI (if installed at `/opt/intel/oneapi`)
- Supports JCMwave (if installed at `~/.jcmwave`)
- Supports StoBe DFT (if installed at `/bin/stobe`)
- Uses `dircolors` for ls colors
- Clipboard: `xclip` or `xsel`

## Customization

### Adding Local Overrides

Create `~/.zshrc.local` or `~/.bashrc.local` for machine-specific settings (not tracked in git).

Add to `.zshrc` or `.bashrc`:

```bash
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
```

### Switching Back to Oh-My-Posh

The Catppuccin Oh-My-Posh theme is preserved. To switch back:

1. Install oh-my-posh: `brew install oh-my-posh`
2. Edit `.zshrc` and replace the starship block with:

```bash
eval "$(oh-my-posh init zsh --config $DOTFILES/catppuccin/catppuccin_frappe.omp.json)"
```

## Updating

```bash
cd ~/dotfiles
git pull
source ~/.zshrc
```

## License

MIT
