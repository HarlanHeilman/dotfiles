#!/usr/bin/env zsh

export DOTFILES="${DOTFILES:-$HOME/dotfiles}"

_OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    _OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    _OS="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    _OS="windows"
fi

for _zsh_module in env path aliases; do
    _zsh_module_path="$DOTFILES/zsh/${_zsh_module}.zsh"
    if [[ -r "$_zsh_module_path" ]]; then
        source "$_zsh_module_path"
    fi
done
unset _zsh_module _zsh_module_path

HISTFILE="$HOME/.zsh_history"
HISTSIZE=100000
SAVEHIST=100000
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt SHARE_HISTORY
setopt APPEND_HISTORY
setopt INC_APPEND_HISTORY

setopt AUTO_CD
setopt CORRECT
setopt NO_BEEP

bindkey -v
export KEYTIMEOUT=1

autoload -Uz compinit && compinit
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' menu select

export STARSHIP_CONFIG="$DOTFILES/starship/starship.toml"
if command -v starship &> /dev/null; then
    eval "$(starship init zsh)"
fi

if [[ -f "$DOTFILES/fzf/init.sh" ]]; then
    source "$DOTFILES/fzf/init.sh"
fi

if command -v fzf &> /dev/null; then
    if [[ "$_OS" == "macos" ]]; then
        if [[ -f "/opt/homebrew/opt/fzf/shell/completion.zsh" ]]; then
            source "/opt/homebrew/opt/fzf/shell/completion.zsh"
        fi
        if [[ -f "/opt/homebrew/opt/fzf/shell/key-bindings.zsh" ]]; then
            source "/opt/homebrew/opt/fzf/shell/key-bindings.zsh"
        fi
    elif [[ "$_OS" == "linux" ]]; then
        if [[ -f "/usr/share/fzf/completion.zsh" ]]; then
            source "/usr/share/fzf/completion.zsh"
        fi
        if [[ -f "/usr/share/fzf/key-bindings.zsh" ]]; then
            source "/usr/share/fzf/key-bindings.zsh"
        fi
    fi
fi

[[ -r "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"

[[ -r "$HOME/.bun/_bun" ]] && source "$HOME/.bun/_bun"
