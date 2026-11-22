set -gx DOTFILES "$HOME/dotfiles"

set -gx _OS unknown
switch (uname -s)
    case Darwin
        set -gx _OS macos
    case Linux
        set -gx _OS linux
    case CYGWIN'*' MSYS'*' MINGW'*'
        set -gx _OS windows
end

set -g __dotfiles_fish_dir "$DOTFILES/fish"
set -g fish_function_path "$__dotfiles_fish_dir/functions" $fish_function_path

for __dotfiles_module in env path aliases
    set -l __dotfiles_module_path "$__dotfiles_fish_dir/$__dotfiles_module.fish"
    if test -r $__dotfiles_module_path
        source $__dotfiles_module_path
    end
end
set -e __dotfiles_module __dotfiles_module_path

set -g fish_history_size 100000
set -g fish_greeting

fish_vi_key_bindings
set -g fish_escape_delay_ms 10

set -g fish_cursor_default block
set -g fish_cursor_insert block
set -g fish_cursor_replace block
set -g fish_cursor_replace_one block
set -g fish_cursor_visual block
set -g fish_cursor_normal block

set -gx STARSHIP_CONFIG "$DOTFILES/starship/starship.toml"
if type -q starship
    starship init fish | source
    function fish_mode_prompt
    end
end

# zoxide: provides __zoxide_z/__zoxide_zi, used by functions/cd.fish (cd, cdi)
if type -q zoxide
    zoxide init fish --no-cmd | source
end

if test -f "$DOTFILES/fish/fzf.fish"
    source "$DOTFILES/fish/fzf.fish"
end

if type -q fzf
    if test "$_OS" = macos
        if test -f /opt/homebrew/opt/fzf/shell/key-bindings.fish
            source /opt/homebrew/opt/fzf/shell/key-bindings.fish
        end
    else if test "$_OS" = linux
        if test -f /usr/share/fzf/key-bindings.fish
            source /usr/share/fzf/key-bindings.fish
        end
    end
end

# atuin: Ctrl-R history search (after fzf so it wins; Up arrow stays plain history)
if type -q atuin
    atuin init fish --disable-up-arrow | source
end

# mise: per-project tool versions (e.g. node 24 from .node-version). Secrets stay in infisical.
if type -q mise
    mise activate fish | source
end

if test -r "$HOME/.config/fish/config.local.fish"
    source "$HOME/.config/fish/config.local.fish"
end
