#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Dotfiles installation script.

Usage:
    uv run install.py [--dry-run] [--no-backup] [--install-deps]

Options:
    --dry-run       Show what would be done without making changes
    --no-backup     Skip backing up existing files
    --install-deps  Install dependencies (starship, zoxide, fzf, bat, eza, ripgrep)
"""
from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class OS(Enum):
    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


@dataclass
class Config:
    dry_run: bool = False
    backup: bool = True
    install_deps: bool = False


def detect_os() -> OS:
    system = platform.system().lower()
    if system == "darwin":
        return OS.MACOS
    elif system == "linux":
        return OS.LINUX
    elif system == "windows":
        return OS.WINDOWS
    return OS.UNKNOWN


def get_dotfiles_dir() -> Path:
    return Path(__file__).parent.resolve()


def get_home_dir() -> Path:
    return Path.home()


def get_config_dir() -> Path:
    if detect_os() == OS.MACOS:
        return get_home_dir() / ".config"
    elif detect_os() == OS.LINUX:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config)
        return get_home_dir() / ".config"
    elif detect_os() == OS.WINDOWS:
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata)
        return get_home_dir() / "AppData" / "Roaming"
    return get_home_dir() / ".config"


def log_info(msg: str) -> None:
    print(f"  [INFO] {msg}")


def log_success(msg: str) -> None:
    print(f"  [OK] {msg}")


def log_warning(msg: str) -> None:
    print(f"  [WARN] {msg}")


def log_error(msg: str) -> None:
    print(f"  [ERROR] {msg}")


def log_action(msg: str) -> None:
    print(f"  [ACTION] {msg}")


def backup_file(path: Path, config: Config) -> bool:
    if not path.exists():
        return True

    if not config.backup:
        return True

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f"{path.suffix}.backup_{timestamp}")

    if config.dry_run:
        log_action(f"Would backup {path} -> {backup_path}")
        return True

    try:
        if path.is_symlink():
            backup_path.symlink_to(path.readlink())
        elif path.is_file():
            shutil.copy2(path, backup_path)
        elif path.is_dir():
            shutil.copytree(path, backup_path)
        log_success(f"Backed up {path} -> {backup_path}")
        return True
    except OSError as e:
        log_error(f"Failed to backup {path}: {e}")
        return False


def create_symlink(source: Path, target: Path, config: Config) -> bool:
    if not source.exists():
        log_error(f"Source does not exist: {source}")
        return False

    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.readlink() == source:
            log_info(f"Symlink already correct: {target}")
            return True

        if not backup_file(target, config):
            return False

        if not config.dry_run:
            if target.is_symlink() or target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)

    if config.dry_run:
        log_action(f"Would symlink {target} -> {source}")
        return True

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source)
        log_success(f"Symlinked {target} -> {source}")
        return True
    except OSError as e:
        log_error(f"Failed to create symlink {target}: {e}")
        return False


def run_command(cmd: Sequence[str], config: Config) -> bool:
    cmd_str = " ".join(cmd)
    if config.dry_run:
        log_action(f"Would run: {cmd_str}")
        return True

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            log_success(f"Ran: {cmd_str}")
            return True
        else:
            log_error(f"Command failed: {cmd_str}")
            if result.stderr:
                log_error(result.stderr.strip())
            return False
    except FileNotFoundError:
        log_error(f"Command not found: {cmd[0]}")
        return False


def check_command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def install_homebrew_packages(packages: list[str], config: Config) -> bool:
    if not check_command_exists("brew"):
        log_warning("Homebrew not found. Install from https://brew.sh")
        return False

    for package in packages:
        result = subprocess.run(
            ["brew", "list", package],
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            log_info(f"{package} already installed")
            continue
        run_command(["brew", "install", package], config)
    return True


def install_apt_packages(packages: list[str], config: Config) -> bool:
    if not check_command_exists("apt"):
        log_warning("apt not found")
        return False

    for package in packages:
        run_command(["sudo", "apt", "install", "-y", package], config)
    return True


def install_dependencies(config: Config) -> None:
    print("\n[2/3] Installing dependencies...")

    detected_os = detect_os()
    packages = ["starship", "zoxide", "fzf", "bat", "eza", "ripgrep", "fd"]

    if detected_os == OS.MACOS:
        install_homebrew_packages(packages, config)
    elif detected_os == OS.LINUX:
        if check_command_exists("brew"):
            install_homebrew_packages(packages, config)
        elif check_command_exists("apt"):
            apt_packages = ["fzf", "bat", "ripgrep", "fd-find"]
            install_apt_packages(apt_packages, config)
            log_info("For starship and eza on Linux, use:")
            log_info("  curl -sS https://starship.rs/install.sh | sh")
            log_info("  cargo install eza")
        else:
            log_warning("No supported package manager found")
    else:
        log_warning(f"Dependency installation not supported on {detected_os.value}")


def setup_bin_scripts(dotfiles: Path, home: Path, config: Config) -> None:
    """Symlink executable helpers from ``dotfiles/bin`` into ``~/.local/bin``.

    Parameters
    ----------
    dotfiles : Path
        Root of the dotfiles repository.
    home : Path
        User home directory.
    config : Config
        Installer configuration.

    Returns
    -------
    None
        Side effect only: creates symlinks for each executable script.
    """
    bin_dir = dotfiles / "bin"
    if not bin_dir.is_dir():
        return

    local_bin = home / ".local" / "bin"
    if not config.dry_run:
        local_bin.mkdir(parents=True, exist_ok=True)

    for script in sorted(bin_dir.iterdir()):
        if not script.is_file():
            continue
        if not os.access(script, os.X_OK):
            if not config.dry_run:
                script.chmod(script.stat().st_mode | 0o111)
        create_symlink(script, local_bin / script.name, config)


def ensure_ssh_config_include(ssh_config: Path, config: Config) -> None:
    """Ensure ``~/.ssh/config`` includes ``config.d/*.conf`` fragments.

    Parameters
    ----------
    ssh_config : Path
        Path to the user OpenSSH config file.
    config : Config
        Installer configuration.

    Returns
    -------
    None
        Side effect only: creates or prepends an Include directive.
    """
    include_line = "Include config.d/*.conf"
    include_re = re.compile(r"^\s*Include\s+config\.d/\*\.conf\s*$")

    if config.dry_run:
        if not ssh_config.exists():
            log_action(f"Would create {ssh_config} with {include_line}")
        else:
            text = ssh_config.read_text(encoding="utf-8")
            if not any(include_re.match(line) for line in text.splitlines()):
                log_action(f"Would prepend {include_line} to {ssh_config}")
            else:
                log_info(f"Include already present in {ssh_config}")
        return

    ssh_config.parent.mkdir(parents=True, exist_ok=True)
    if not ssh_config.exists():
        ssh_config.write_text(include_line + "\n", encoding="utf-8")
        ssh_config.chmod(0o600)
        log_success(f"Created {ssh_config} with Include")
        return

    text = ssh_config.read_text(encoding="utf-8")
    if any(include_re.match(line) for line in text.splitlines()):
        log_info(f"Include already present in {ssh_config}")
        return

    ssh_config.write_text(include_line + "\n\n" + text, encoding="utf-8")
    ssh_config.chmod(0o600)
    log_success(f"Prepended Include to {ssh_config}")


def setup_ssh_configs(dotfiles: Path, home: Path, config: Config) -> None:
    """Install host-scoped SSH client policy and control-socket directory.

    Links ``dotfiles/ssh/config.d/*.conf`` into ``~/.ssh/config.d``, ensures
    ``~/.ssh/config`` includes those fragments, and creates
    ``~/.ssh/control`` for ``ControlMaster`` multiplexing. Host fragments
    select per-target identities; defaults enable IdentitiesOnly, agent
    loading, macOS Keychain passphrase reuse, and an 8h control persist.

    Parameters
    ----------
    dotfiles : Path
        Root of the dotfiles repository.
    home : Path
        User home directory.
    config : Config
        Installer configuration.

    Returns
    -------
    None
        Side effect only: installs SSH config fragments, Include, and
        control directory.
    """
    print("\n[ssh] Setting up host-scoped SSH client policy...")

    src_dir = dotfiles / "ssh" / "config.d"
    if not src_dir.is_dir():
        log_warning(f"Missing SSH config fragments: {src_dir}")
        return

    ssh_dir = home / ".ssh"
    config_d = ssh_dir / "config.d"
    control_dir = ssh_dir / "control"
    if not config.dry_run:
        ssh_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        config_d.mkdir(mode=0o700, parents=True, exist_ok=True)
        control_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(ssh_dir, 0o700)
        os.chmod(control_dir, 0o700)
    else:
        log_action(f"Would ensure {control_dir} exists (mode 0700)")

    current_os = detect_os()
    for src in sorted(src_dir.glob("*.conf")):
        if src.name == "01-macos-keychain.conf" and current_os != OS.MACOS:
            continue
        create_symlink(src, config_d / src.name, config)

    if current_os != OS.MACOS:
        stale_macos = config_d / "01-macos-keychain.conf"
        if stale_macos.exists() or stale_macos.is_symlink():
            if config.dry_run:
                log_action(f"Would remove non-macOS fragment {stale_macos}")
            else:
                stale_macos.unlink()
                log_success(f"Removed non-macOS fragment {stale_macos}")

    ensure_ssh_config_include(ssh_dir / "config", config)


def setup_macos_launch_agents(dotfiles: Path, home: Path, config: Config) -> None:
    """Install LaunchAgents that set GUI-session env vars on every login.

    Currently used so Zed sees ``LOCAL_NOTEBOOK_DEV=1`` without a manual
    ``launchctl setenv`` after each reboot. Plists are copied (not symlinked)
    because launchd can be picky about symlinked agents. The variable is also
    set immediately so the current session works without re-login.

    Parameters
    ----------
    dotfiles : Path
        Root of the dotfiles repository.
    home : Path
        User home directory.
    config : Config
        Installer configuration.

    Returns
    -------
    None
        Side effect only: copies plists and sets the env var. No-op off macOS.
    """
    if detect_os() != OS.MACOS:
        return

    print("\n[launchd] Setting up macOS LaunchAgents...")

    src_dir = dotfiles / "launchd"
    if not src_dir.is_dir():
        log_warning(f"Missing LaunchAgents directory: {src_dir}")
        return

    agents_dir = home / "Library" / "LaunchAgents"
    for src in sorted(src_dir.glob("*.plist")):
        dest = agents_dir / src.name
        if dest.is_file() and not dest.is_symlink() and dest.read_bytes() == src.read_bytes():
            log_info(f"LaunchAgent already up to date: {dest}")
            continue
        if config.dry_run:
            log_action(f"Would copy {src} -> {dest}")
            continue
        if not backup_file(dest, config):
            continue
        try:
            agents_dir.mkdir(parents=True, exist_ok=True)
            if dest.is_symlink():
                dest.unlink()
            shutil.copy2(src, dest)
            log_success(f"Installed LaunchAgent: {dest}")
        except OSError as e:
            log_error(f"Failed to install {dest}: {e}")

    run_command(["launchctl", "setenv", "LOCAL_NOTEBOOK_DEV", "1"], config)


def setup_shell_configs(dotfiles: Path, home: Path, config: Config) -> None:
    print("\n[1/3] Setting up shell configurations...")

    fish_path = shutil.which("fish")
    if not fish_path:
        log_warning("fish not found; install it first (brew install fish)")
        return
    shells = Path("/etc/shells")
    if shells.is_file() and fish_path not in shells.read_text().split():
        log_info(f"Add fish to /etc/shells: echo {fish_path} | sudo tee -a /etc/shells")
    if os.environ.get("SHELL") != fish_path:
        log_info(f"Make fish your login shell: chsh -s {fish_path}")


def setup_env_local_templates(dotfiles: Path, config: Config) -> None:
    """Seed gitignored local env overlays from committed example templates.

    Copies each ``*.example.*`` env template into the corresponding
    ``env.local.*`` path when that local file is missing. Existing local
    files are left untouched so machine secrets are never overwritten.

    Parameters
    ----------
    dotfiles : Path
        Root of the dotfiles repository.
    config : Config
        Installer configuration; when ``dry_run`` is true, only logs the
        intended copies.

    Returns
    -------
    None
        Side effect only: creates missing local env overlay files.
    """
    pairs = (
        (
            dotfiles / "fish" / "env.local.example.fish",
            dotfiles / "fish" / "env.local.fish",
        ),
    )
    for example, local in pairs:
        if not example.is_file():
            log_warning(f"Missing env template: {example}")
            continue
        if local.exists():
            log_info(f"Local env already present: {local}")
            continue
        if config.dry_run:
            log_action(f"Would copy {example} -> {local}")
            continue
        try:
            shutil.copy2(example, local)
            log_success(f"Created local env from template: {local}")
            log_warning(f"Fill in secret values in {local}")
        except OSError as e:
            log_error(f"Failed to create {local}: {e}")


def setup_fish_configs(dotfiles: Path, config_dir: Path, config: Config) -> None:
    fish_dir = config_dir / "fish"
    fish_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(dotfiles / "fish" / "config.fish", fish_dir / "config.fish", config)

    functions_dir = fish_dir / "functions"
    functions_dir.mkdir(parents=True, exist_ok=True)
    dotfiles_functions = dotfiles / "fish" / "functions"
    if dotfiles_functions.is_dir():
        for fish_func in sorted(dotfiles_functions.glob("*.fish")):
            create_symlink(fish_func, functions_dir / fish_func.name, config)

    completions_dir = fish_dir / "completions"
    completions_dir.mkdir(parents=True, exist_ok=True)
    dotfiles_completions = dotfiles / "fish" / "completions"
    if dotfiles_completions.is_dir():
        for fish_completion in sorted(dotfiles_completions.glob("*.fish")):
            create_symlink(
                fish_completion,
                completions_dir / fish_completion.name,
                config,
            )


def setup_tool_configs(dotfiles: Path, config_dir: Path, config: Config) -> None:
    print("\n[3/3] Setting up tool configurations...")

    starship_config = config_dir / "starship.toml"
    create_symlink(dotfiles / "starship" / "starship.toml", starship_config, config)

    lazygit_dir = config_dir / "lazygit"
    lazygit_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(
        dotfiles / "lazygit" / "config.yml",
        lazygit_dir / "config.yml",
        config,
    )

    uv_config_dir = config_dir / "uv"
    uv_config_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(dotfiles / "uv" / "uv.toml", uv_config_dir / "uv.toml", config)


def setup_terminal_and_cli_configs(dotfiles: Path, config_dir: Path, config: Config) -> None:
    """Symlink ghostty, kitty, atuin, mise configs and include the delta gitconfig."""
    print("\n[cli] Setting up terminal and CLI tool configs...")
    links = (
        ("ghostty/config", "ghostty/config"),
        ("kitty/kitty.conf", "kitty/kitty.conf"),
        ("kitty/dark-theme.auto.conf", "kitty/dark-theme.auto.conf"),
        ("kitty/light-theme.auto.conf", "kitty/light-theme.auto.conf"),
        ("kitty/no-preference-theme.auto.conf", "kitty/no-preference-theme.auto.conf"),
        ("atuin/config.toml", "atuin/config.toml"),
        ("mise/config.toml", "mise/config.toml"),
        ("ruff/ruff.toml", "ruff/ruff.toml"),
        ("agents/opencode.json", "opencode/opencode.json"),
    )
    for src, dest in links:
        dest_path = config_dir / dest
        if not config.dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
        create_symlink(dotfiles / src, dest_path, config)

    home = config_dir.parent
    agent_links = (
        ("claude/settings.json", home / ".claude" / "settings.json"),
        ("agents/AGENTS.md", home / ".claude" / "CLAUDE.md"),
        ("agents/AGENTS.md", home / ".agents" / "AGENTS.md"),
        ("agents/AGENTS.md", config_dir / "opencode" / "AGENTS.md"),
    )
    for src, dest_path in agent_links:
        if not config.dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
        create_symlink(dotfiles / src, dest_path, config)

    cargo_cfg = home / ".cargo" / "config.toml"
    if not config.dry_run:
        cargo_cfg.parent.mkdir(parents=True, exist_ok=True)
    create_symlink(dotfiles / "cargo" / "config.toml", cargo_cfg, config)

    # Shared skills: dotfiles/agents/skills/* -> ~/.agents/skills/, then
    # everything in ~/.agents/skills/ -> ~/.claude/skills/ (opencode reads ~/.agents).
    shared = home / ".agents" / "skills"
    claude_skills = home / ".claude" / "skills"
    if not config.dry_run:
        shared.mkdir(parents=True, exist_ok=True)
        claude_skills.mkdir(parents=True, exist_ok=True)
    custom = dotfiles / "agents" / "skills"
    for skill in sorted(p for p in custom.iterdir() if p.is_dir()):
        create_symlink(skill, shared / skill.name, config)
    if shared.is_dir():
        for skill in sorted(p for p in shared.iterdir() if p.is_dir()):
            if not (claude_skills / skill.name).exists():
                create_symlink(skill, claude_skills / skill.name, config)

    existing = subprocess.run(
        ["git", "config", "--global", "--get-all", "include.path"],
        capture_output=True,
        text=True,
    ).stdout.split()
    for name in ("defaults.gitconfig", "delta.gitconfig"):
        include = str(dotfiles / "git" / name)
        if include not in existing:
            run_command(
                ["git", "config", "--global", "--add", "include.path", include],
                config,
            )


def setup_zed_configs(dotfiles: Path, config_dir: Path, config: Config) -> None:
    """Symlink Zed settings, keymap, and snippets into the Zed config dir.

    Files are linked individually so Zed's own state (prompt DB, themes)
    in ``~/.config/zed`` is left alone.

    Parameters
    ----------
    dotfiles : Path
        Root of the dotfiles repository.
    config_dir : Path
        User config directory (``~/.config`` on macOS/Linux).
    config : Config
        Installer configuration.

    Returns
    -------
    None
        Side effect only: creates symlinks for Zed config files.
    """
    print("\n[zed] Setting up Zed configuration...")

    src_dir = dotfiles / "zed"
    if not src_dir.is_dir():
        log_warning(f"Missing Zed config directory: {src_dir}")
        return

    zed_dir = config_dir / "zed"
    if not config.dry_run:
        zed_dir.mkdir(parents=True, exist_ok=True)

    for name in ("settings.json", "keymap.json"):
        create_symlink(src_dir / name, zed_dir / name, config)

    snippets_src = src_dir / "snippets"
    if snippets_src.is_dir():
        snippets_dir = zed_dir / "snippets"
        if not config.dry_run:
            snippets_dir.mkdir(parents=True, exist_ok=True)
        for snippet in sorted(snippets_src.glob("*.json")):
            create_symlink(snippet, snippets_dir / snippet.name, config)


def print_header() -> None:
    print("=" * 60)
    print("  Dotfiles Installation Script")
    print("=" * 60)


def print_summary(dotfiles: Path, config: Config) -> None:
    detected_os = detect_os()
    print(f"\n  OS Detected:    {detected_os.value}")
    print(f"  Dotfiles Path:  {dotfiles}")
    print(f"  Dry Run:        {config.dry_run}")
    print(f"  Backup:         {config.backup}")
    print(f"  Install Deps:   {config.install_deps}")


@dataclass
class Tool:
    name: str
    command: str
    required: bool
    brew: str
    apt: str | None
    description: str


TOOLS: list[Tool] = [
    Tool("Starship", "starship", True, "starship", None, "Cross-shell prompt"),
    Tool("uv", "uv", True, "uv", None, "Python package manager"),
    Tool("zoxide", "zoxide", False, "zoxide", None, "Smarter cd (replaces cd)"),
    Tool("fzf", "fzf", False, "fzf", "fzf", "Fuzzy finder"),
    Tool("bat", "bat", False, "bat", "bat", "Cat replacement with syntax highlighting"),
    Tool("eza", "eza", False, "eza", None, "Tree and extended file listing"),
    Tool("ripgrep", "rg", False, "ripgrep", "ripgrep", "Fast grep replacement"),
    Tool("fd", "fd", False, "fd", "fd-find", "Fast find replacement"),
    Tool("lazygit", "lazygit", False, "lazygit", None, "Terminal UI for git"),
    Tool("neovim", "nvim", False, "neovim", "neovim", "Vim-based text editor"),
    Tool("fish", "fish", True, "fish", "fish", "Friendly interactive shell"),
]


def check_tools() -> tuple[list[Tool], list[Tool]]:
    installed: list[Tool] = []
    missing: list[Tool] = []

    for tool in TOOLS:
        if check_command_exists(tool.command):
            installed.append(tool)
        else:
            missing.append(tool)

    return installed, missing


def print_tool_status() -> tuple[list[Tool], list[Tool]]:
    print("\n" + "-" * 60)
    print("  Tool Status")
    print("-" * 60)

    installed, missing = check_tools()

    if installed:
        print("\n  Installed:")
        for tool in installed:
            marker = "*" if tool.required else " "
            print(f"    [{marker}] {tool.name:<12} - {tool.description}")

    if missing:
        print("\n  Missing:")
        for tool in missing:
            marker = "*" if tool.required else " "
            print(f"    [{marker}] {tool.name:<12} - {tool.description}")

    print("\n  [*] = Required")

    return installed, missing


def print_install_commands(missing: list[Tool]) -> None:
    if not missing:
        return

    detected_os = detect_os()

    print("\n" + "-" * 60)
    print("  Installation Commands")
    print("-" * 60)

    required = [t for t in missing if t.required]
    optional = [t for t in missing if not t.required]

    if detected_os == OS.MACOS:
        if required:
            brew_pkgs = " ".join(t.brew.replace(" (cask)", "") for t in required if "(cask)" not in t.brew)
            cask_pkgs = [t.brew.replace(" (cask)", "") for t in required if "(cask)" in t.brew]
            print("\n  Required (install these first):")
            if brew_pkgs:
                print(f"    brew install {brew_pkgs}")
            for pkg in cask_pkgs:
                print(f"    brew install --cask {pkg}")

        if optional:
            brew_pkgs = " ".join(t.brew.replace(" (cask)", "") for t in optional if "(cask)" not in t.brew)
            cask_pkgs = [t.brew.replace(" (cask)", "") for t in optional if "(cask)" in t.brew]
            print("\n  Recommended:")
            if brew_pkgs:
                print(f"    brew install {brew_pkgs}")
            for pkg in cask_pkgs:
                print(f"    brew install --cask {pkg}")

    elif detected_os == OS.LINUX:
        apt_available = [t for t in missing if t.apt]
        manual_install = [t for t in missing if not t.apt]

        if apt_available:
            required_apt = [t for t in apt_available if t.required]
            optional_apt = [t for t in apt_available if not t.required]

            if required_apt:
                apt_pkgs = " ".join(t.apt for t in required_apt if t.apt)
                print("\n  Required (apt):")
                print(f"    sudo apt install {apt_pkgs}")

            if optional_apt:
                apt_pkgs = " ".join(t.apt for t in optional_apt if t.apt)
                print("\n  Recommended (apt):")
                print(f"    sudo apt install {apt_pkgs}")

        if manual_install:
            print("\n  Manual installation required:")
            for tool in manual_install:
                if tool.name == "Starship":
                    print(f"    {tool.name}: curl -sS https://starship.rs/install.sh | sh")
                elif tool.name == "eza":
                    print(f"    {tool.name}: cargo install eza")
                elif tool.name == "uv":
                    print(f"    {tool.name}: curl -LsSf https://astral.sh/uv/install.sh | sh")
                else:
                    print(f"    {tool.name}: See https://github.com/search?q={tool.command}")


def print_post_install(missing: list[Tool]) -> None:
    print("\n" + "=" * 60)
    print("  Installation Complete")
    print("=" * 60)

    required_missing = [t for t in missing if t.required]
    if required_missing:
        print("\n  WARNING: Required tools are missing!")
        print("  Install them before using these dotfiles.")

    print("\n  Next steps:")
    step = 1
    if required_missing:
        print(f"    {step}. Install missing required tools (see commands above)")
        step += 1
    print(f"    {step}. Open a new terminal or run: source ~/.config/fish/config.fish (or just open a new fish terminal)")
    step += 1
    print(f"    {step}. Ensure a Nerd Font is installed for icons")
    step += 1
    print(
        f"    {step}. Client machines: auth hduva | auth perlmutter | auth user@host"
    )
    step += 1
    print(
        f"    {step}. CA-fleet hosts only: run workstation-ca-setup (sudo) once per machine"
    )

    print("\n  Recommended Nerd Fonts:")
    print("    - FiraCode Nerd Font")
    print("    - JetBrainsMono Nerd Font")
    print("    - Hack Nerd Font")
    print("\n  Download from: https://www.nerdfonts.com/font-downloads")


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Install dotfiles configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backing up existing files",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install dependencies (starship, zoxide, fzf, bat, eza, ripgrep)",
    )

    args = parser.parse_args()

    return Config(
        dry_run=args.dry_run,
        backup=not args.no_backup,
        install_deps=args.install_deps,
    )


def main() -> int:
    config = parse_args()

    print_header()

    dotfiles = get_dotfiles_dir()
    home = get_home_dir()
    config_dir = get_config_dir()

    print_summary(dotfiles, config)

    _, missing = print_tool_status()

    if config.dry_run:
        print("\n  [DRY RUN MODE - No changes will be made]")

    setup_shell_configs(dotfiles, home, config)
    setup_env_local_templates(dotfiles, config)
    setup_fish_configs(dotfiles, config_dir, config)
    setup_terminal_and_cli_configs(dotfiles, config_dir, config)
    setup_bin_scripts(dotfiles, home, config)
    setup_ssh_configs(dotfiles, home, config)
    setup_macos_launch_agents(dotfiles, home, config)
    setup_zed_configs(dotfiles, config_dir, config)

    if config.install_deps:
        install_dependencies(config)

    setup_tool_configs(dotfiles, config_dir, config)

    if missing:
        print_install_commands(missing)

    if not config.dry_run:
        print_post_install(missing)

    return 0


if __name__ == "__main__":
    sys.exit(main())
