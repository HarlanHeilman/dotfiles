set -gx FZF_DEFAULT_OPTS "\
--color=fg:-1,bg:-1,fg+:-1,bg+:-1,hl:blue,hl+:blue,prompt:blue,pointer:magenta \
--color=marker:green,spinner:magenta,info:bright-black,header:bright-black \
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
