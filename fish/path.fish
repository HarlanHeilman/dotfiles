function __dotfiles_import_sh_env --description 'Import variables from a POSIX shell file'
    set -l sh_file $argv[1]
    if not test -f $sh_file
        return 1
    end
    set -l skip_vars PWD OLDPWD SHLVL _ HOME USER SHELL TERM LOGNAME
    set -l q_file (string escape --style=var $sh_file)
    for line in (bash -c "source $q_file >/dev/null 2>&1; env")
        if string match -qr '^[A-Za-z_][A-Za-z0-9_]*=' -- $line
            set -l parts (string split -m 1 '=' -- $line)
            if contains -i $parts[1] $skip_vars
                continue
            end
            set -gx $parts[1] $parts[2]
        end
    end
end

fish_add_path $HOME/.local/bin
fish_add_path $HOME/.cargo/bin

if test "$_OS" = macos
    fish_add_path /opt/homebrew/bin /opt/homebrew/sbin
    if test -f /opt/homebrew/bin/brew
        eval (/opt/homebrew/bin/brew shellenv fish)
    end
end

if test "$_OS" = linux
    fish_add_path /opt/nvim-linux64/bin

    if test -f /opt/intel/oneapi/setvars.sh
        __dotfiles_import_sh_env /opt/intel/oneapi/setvars.sh
    end

    if test -d /bin/stobe/Source
        fish_add_path /bin/stobe/Source
    end

    if test -d "$HOME/.jcmwave"
        fish_add_path "$HOME/.jcmwave/bin"
    end
end

if test -d "$HOME/.bun"
    set -gx BUN_INSTALL "$HOME/.bun"
    fish_add_path "$BUN_INSTALL/bin"
end

functions -e __dotfiles_import_sh_env
