#!/usr/bin/env bash

_OS="unknown"
case "$OSTYPE" in
    darwin*)  _OS="macos" ;;
    linux*)   _OS="linux" ;;
    msys*|cygwin*) _OS="windows" ;;
esac

export DOTFILES="$HOME/dotfiles"
export PROJECTS="$HOME/projects"

export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"

if [[ "$_OS" == "macos" ]]; then
    export PATH="/opt/homebrew/bin:$PATH"
    export PATH="/opt/homebrew/sbin:$PATH"
    
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

if [[ "$_OS" == "linux" ]]; then
    export PATH="/opt/nvim-linux64/bin:$PATH"
    
    if [[ -f "/opt/intel/oneapi/setvars.sh" ]]; then
        source /opt/intel/oneapi/setvars.sh > /dev/null 2>&1
    fi
    
    if [[ -d "/bin/stobe/Source" ]]; then
        export PATH="/bin/stobe/Source:$PATH"
        export STOBE="/bin/stobe/"
        export STOBE_BASIS="${STOBE}Basis/"
        alias dft='rm -rf *.inp && rm -rf *.out && chmod +x **.run && ./${PWD##*/}gnd.run && ./${PWD##*/}exc.run && ./${PWD##*/}tp.run && ./${PWD##*/}xas.run'
    fi
    
    if [[ -d "$HOME/.jcmwave" ]]; then
        export JCMROOT="$HOME/.jcmwave/"
        export JCMPYTHON="${JCMROOT}ThirdPartySupport/python/"
        export PYTHONPATH="${PYTHONPATH}:${JCMPYTHON}"
        export PATH="${PATH}:$HOME/.jcmwave/bin"
    fi
fi

if [[ -d "$HOME/.bun" ]]; then
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
fi

if [[ -f "$HOME/.local/bin/env" ]]; then
    source "$HOME/.local/bin/env"
fi

if [[ -f "$HOME/.cargo/env" ]]; then
    source "$HOME/.cargo/env"
fi

export POLARS_VERBOSE=1
export RUST_BACKTRACE="full"
export RUST_LOG="warn"
export CARGO_PROFILE_RELEASE_BUILD_OVERRIDE_DEBUG=true

export AWS_DEFAULT_PROFILE='lbl'

HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=100000
HISTFILESIZE=200000

shopt -s checkwinsize

export STARSHIP_CONFIG="$DOTFILES/starship/starship.toml"
if command -v starship &> /dev/null; then
    eval "$(starship init bash)"
fi

if [[ -f "$DOTFILES/fzf/init.sh" ]]; then
    source "$DOTFILES/fzf/init.sh"
fi

if command -v fzf &> /dev/null; then
    if [[ "$_OS" == "macos" ]]; then
        if [[ -f "/opt/homebrew/opt/fzf/shell/completion.bash" ]]; then
            source "/opt/homebrew/opt/fzf/shell/completion.bash"
        fi
        if [[ -f "/opt/homebrew/opt/fzf/shell/key-bindings.bash" ]]; then
            source "/opt/homebrew/opt/fzf/shell/key-bindings.bash"
        fi
    elif [[ "$_OS" == "linux" ]]; then
        if [[ -f "/usr/share/fzf/completion.bash" ]]; then
            source "/usr/share/fzf/completion.bash"
        fi
        if [[ -f "/usr/share/fzf/key-bindings.bash" ]]; then
            source "/usr/share/fzf/key-bindings.bash"
        fi
        if [[ -f "/usr/share/bash-completion/completions/fzf" ]]; then
            source "/usr/share/bash-completion/completions/fzf"
        fi
    fi
fi

if [[ "$_OS" == "macos" ]]; then
    alias ls='ls -G'
else
    if [[ -x /usr/bin/dircolors ]]; then
        test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    fi
    alias ls='ls --color=auto'
fi
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

if command -v rg &> /dev/null; then
    alias rg='rg --smart-case'
fi

if command -v bat &> /dev/null; then
    alias cat='bat --style=plain'
    alias catp='bat'
fi

if command -v eza &> /dev/null; then
    alias tree='eza --tree --level=2 --icons --group-directories-first'
    alias tree3='eza --tree --level=3 --icons --group-directories-first'
    alias lx='eza -la --icons --group-directories-first --git'
fi

alias vim='nvim'
alias v='nvim'
alias c='zed'

alias dot='cd $DOTFILES'
alias proj='cd $PROJECTS'

gc() {
    if [[ -z "$1" ]]; then
        echo "Commit message is required"
        return 1
    fi
    git add .
    git commit -m "$1"
    git push -u origin --tags
    git push
}

alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline -n 20'
alias gp='git pull'

alias py='python3'
alias pip='uv pip'

venv() {
    if [[ ! -d ".venv" ]]; then
        uv venv
    fi
    source ./.venv/bin/activate
}

alias activate='source ./.venv/bin/activate'
alias build='venv && maturin develop --uv'

smiles() {
    local smiles_str="$1"
    
    if ! command -v obabel &> /dev/null; then
        echo "obabel not found. Install open-babel first."
        return 1
    fi
    
    local svg=$(obabel -:"$smiles_str" -o svg 2>/dev/null)
    local inchi=$(obabel -:"$smiles_str" -o inchi 2>/dev/null)
    local flattened_svg=$(echo "$svg" | tr -d '\n')
    
    local output="\"image\" : \"$flattened_svg\",\n\"SMILES\": \"$smiles_str\",\n\"InChI\" : \"$inchi\","
    echo "$output"
    
    if [[ "$_OS" == "macos" ]]; then
        echo -e "$output" | pbcopy
    elif command -v xclip &> /dev/null; then
        echo -e "$output" | xclip -selection clipboard
    elif command -v xsel &> /dev/null; then
        echo -e "$output" | xsel --clipboard --input
    else
        echo "No clipboard utility found"
        return 0
    fi
    echo "JSON output copied to clipboard"
}

if [[ "$_OS" == "linux" ]]; then
    if [[ -z "${debian_chroot:-}" ]] && [[ -r /etc/debian_chroot ]]; then
        debian_chroot=$(cat /etc/debian_chroot)
    fi
    
    if [[ -x /usr/bin/lesspipe ]]; then
        eval "$(SHELL=/bin/sh lesspipe)"
    fi
    
    if ! shopt -oq posix; then
        if [[ -f /usr/share/bash-completion/bash_completion ]]; then
            source /usr/share/bash-completion/bash_completion
        elif [[ -f /etc/bash_completion ]]; then
            source /etc/bash_completion
        fi
    fi
    
    if command -v notify-send &> /dev/null; then
        alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
    fi
fi

alias refresh='source ~/.bashrc && clear'
alias edit='nvim ~/.bashrc && refresh'
alias edot='nvim $DOTFILES/.bashrc && refresh'

if [[ -f ~/.bash_aliases ]]; then
    source ~/.bash_aliases
fi
