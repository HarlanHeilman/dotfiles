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
    fi

    if [[ -d "$HOME/.jcmwave" ]]; then
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
