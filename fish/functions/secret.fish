function secret --description 'Personal secrets in the macOS login Keychain (service dotfiles:NAME)'
    set -l cmd $argv[1]
    set -l name $argv[2]
    switch "$cmd"
        case set
            test -n "$name"; or begin; echo "usage: secret set NAME"; return 2; end
            # -w with no value makes `security` prompt on the TTY, so the value never hits argv
            security add-generic-password -U -a $USER -s "dotfiles:$name" -w
        case get
            test -n "$name"; or begin; echo "usage: secret get NAME"; return 2; end
            security find-generic-password -a $USER -s "dotfiles:$name" -w
        case rm
            test -n "$name"; or begin; echo "usage: secret rm NAME"; return 2; end
            security delete-generic-password -a $USER -s "dotfiles:$name" >/dev/null
        case list
            for n in $__keychain_secrets
                if security find-generic-password -a $USER -s "dotfiles:$n" >/dev/null 2>&1
                    echo "$n  (in keychain)"
                else
                    echo "$n  (MISSING)"
                end
            end
        case '*'
            echo "usage: secret set|get|rm NAME | secret list"
            return 2
    end
end
