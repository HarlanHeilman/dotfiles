if test "$_OS" = macos
    alias ls='ls -G'
else
    alias ls='ls --color=auto'
end
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

alias grep='grep --color=auto'

if type -q rg
    alias rg='rg --smart-case'
end

if type -q bat
    alias cat='bat --style=plain'
    alias catp='bat'
end

if type -q eza
    alias tree='eza --tree --level=2 --icons --group-directories-first'
    alias tree3='eza --tree --level=3 --icons --group-directories-first'
    alias lx='eza -la --icons --group-directories-first --git'
end

alias vim='nvim'
alias v='nvim'
alias c='zed'

alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline -n 20'
alias gp='git pull'

alias py='python3'
alias pip='uv pip'

alias activate='source ./.venv/bin/activate.fish'
alias build='venv; and maturin develop --uv'

alias refresh='source ~/.config/fish/config.fish; and clear'
alias edit='nvim ~/.config/fish/config.fish; and refresh'
alias edot="nvim $DOTFILES/fish/config.fish; and refresh"
