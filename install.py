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
    --install-deps  Install dependencies (starship, fzf, bat, eza, ripgrep)
"""
from __future__ import annotations

import argparse
import os
import platform
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
    packages = ["starship", "fzf", "bat", "eza", "ripgrep", "fd"]

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


def setup_shell_configs(dotfiles: Path, home: Path, config: Config) -> None:
    print("\n[1/3] Setting up shell configurations...")

    create_symlink(dotfiles / ".bashrc", home / ".bashrc", config)
    create_symlink(dotfiles / ".zshrc", home / ".zshrc", config)


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
            dotfiles / "zsh" / "env.local.example.zsh",
            dotfiles / "zsh" / "env.local.zsh",
        ),
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
    Tool("fzf", "fzf", False, "fzf", "fzf", "Fuzzy finder"),
    Tool("bat", "bat", False, "bat", "bat", "Cat replacement with syntax highlighting"),
    Tool("eza", "eza", False, "eza", None, "Tree and extended file listing"),
    Tool("ripgrep", "rg", False, "ripgrep", "ripgrep", "Fast grep replacement"),
    Tool("fd", "fd", False, "fd", "fd-find", "Fast find replacement"),
    Tool("lazygit", "lazygit", False, "lazygit", None, "Terminal UI for git"),
    Tool("neovim", "nvim", False, "neovim", "neovim", "Vim-based text editor"),
    Tool("fish", "fish", False, "fish", "fish", "Friendly interactive shell"),
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
    print(f"    {step}. Open a new terminal or run: source ~/.zshrc")
    step += 1
    print(f"    {step}. Ensure a Nerd Font is installed for icons")

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
        help="Install dependencies (starship, fzf, bat, eza, ripgrep)",
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
