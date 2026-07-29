if [[ "$_OS" == "macos" ]]; then
    alias ls='ls -G'
else
    alias ls='ls --color=auto'
fi
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

alias grep='grep --color=auto'

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
        echo "obabel not found. Install with: brew install open-babel"
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

alias refresh='source ~/.zshrc && clear'
alias edit='nvim ~/.zshrc && refresh'
alias edot='nvim $DOTFILES/.zshrc && refresh'

workstation-auth() {
    local user_key="$HOME/.ssh/workstation"
    local host="${WORKSTATION_SSH_HOST:-hduva}"
    local remote_user="${WORKSTATION_SSH_USER:-hduva}"
    local client_setup="${HOME}/.local/bin/workstation-client-setup"
    local cert_out

    if [[ -x "$client_setup" ]]; then
        "$client_setup" || return $?
    elif [[ -x "${DOTFILES:-$HOME/dotfiles}/bin/workstation-client-setup" ]]; then
        "${DOTFILES:-$HOME/dotfiles}/bin/workstation-client-setup" || return $?
    fi

    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"

    if [[ ! -f "$user_key" ]]; then
        ssh-keygen -t ed25519 -f "$user_key" -N '' -C "$(id -un)@client-for-workstation" || return $?
        chmod 600 "$user_key"
        chmod 644 "$user_key.pub"
    fi

    cert_out="$(mktemp)" || return $?

    echo "Authenticating to ${remote_user}@${host} with account password to mint a 1-day cert"
    if ssh \
        -o PreferredAuthentications=password \
        -o PubkeyAuthentication=no \
        -o NumberOfPasswordPrompts=1 \
        -o IdentitiesOnly=yes \
        -l "$remote_user" \
        "$host" \
        '$HOME/.local/bin/workstation-sign' <"${user_key}.pub" >"$cert_out"
    then
        cp "$cert_out" "${user_key}-cert.pub"
        chmod 600 "${user_key}-cert.pub"
        rm -f "$cert_out"
        echo "Successfully obtained ssh key $user_key"
        ssh-keygen -L -f "${user_key}-cert.pub" | grep -i 'Valid:'
        return 0
    fi

    rm -f "$cert_out"
    echo "Failed to obtain workstation cert from $host" >&2
    return 1
}

workstation-cert-status() {
    local cert="$HOME/.ssh/workstation-cert.pub"
    if [[ ! -f "$cert" ]]; then
        echo "No workstation cert found at $cert. Run 'workstation-auth' first."
        return 1
    fi
    ssh-keygen -L -f "$cert" | grep -i 'Valid:'
}
