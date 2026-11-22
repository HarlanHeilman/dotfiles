function cd --wraps=cd --description 'zoxide-aware cd: flags and no-args use the builtin'
    if test (count $argv) -eq 0; or string match -qr -- '^-.+' $argv[1]
        builtin cd $argv
    else
        __zoxide_z $argv
    end
end

function cdi --wraps=__zoxide_zi --description 'Interactive zoxide jump'
    __zoxide_zi $argv
end
