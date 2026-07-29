set -gx FZF_DEFAULT_OPTS "\
--color=bg+:#414559,bg:#303446,spinner:#f2d5cf,hl:#e78284 \
--color=fg:#c6d0f5,header:#e78284,info:#ca9ee6,pointer:#f2d5cf \
--color=marker:#babbf1,fg+:#c6d0f5,prompt:#ca9ee6,hl+:#e78284 \
--color=selected-bg:#51576d \
--multi \
--height=80% \
--layout=reverse \
--info=inline \
--border \
--margin=1 \
--padding=1"

if type -q bat
    set -gx FZF_DEFAULT_OPTS "$FZF_DEFAULT_OPTS --preview 'bat --color=always --style=header,grid --line-range :500 {}'"
end

if type -q fd
    set -gx FZF_DEFAULT_COMMAND 'fd --type f --hidden --follow --exclude .git'
    set -gx FZF_CTRL_T_COMMAND $FZF_DEFAULT_COMMAND
    set -gx FZF_ALT_C_COMMAND 'fd --type d --hidden --follow --exclude .git'
else if type -q rg
    set -gx FZF_DEFAULT_COMMAND 'rg --files --hidden --follow --glob "!.git/*"'
    set -gx FZF_CTRL_T_COMMAND $FZF_DEFAULT_COMMAND
end
