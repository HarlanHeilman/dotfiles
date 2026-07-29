function workstation-auth --description 'Get a 1-day SSH cert to connect to the workstation (account password once)'
    set -l user_key $HOME/.ssh/workstation
    set -l host $WORKSTATION_SSH_HOST
    set -l remote_user $WORKSTATION_SSH_USER
    set -l client_setup $HOME/.local/bin/workstation-client-setup
    set -l remote_sign '$HOME/.local/bin/workstation-sign'

    if test -x $client_setup
        $client_setup
        or return $status
    else if test -x $DOTFILES/bin/workstation-client-setup
        $DOTFILES/bin/workstation-client-setup
        or return $status
    end

    mkdir -p $HOME/.ssh
    chmod 700 $HOME/.ssh

    if not test -f $user_key
        ssh-keygen -t ed25519 -f $user_key -N '' -C (id -un)"@client-for-workstation"
        or return $status
        chmod 600 $user_key
        chmod 644 $user_key.pub
    end

    set -l cert_out (mktemp)
    or return $status

    echo "Authenticating to $remote_user@$host with account password to mint a 1-day cert"
    if ssh \
            -o PreferredAuthentications=password \
            -o PubkeyAuthentication=no \
            -o NumberOfPasswordPrompts=1 \
            -o IdentitiesOnly=yes \
            -l $remote_user \
            $host \
            $remote_sign <$user_key.pub >$cert_out
        cp $cert_out $user_key-cert.pub
        chmod 600 $user_key-cert.pub
        rm -f $cert_out
        echo "Successfully obtained ssh key $user_key"
        ssh-keygen -L -f $user_key-cert.pub | string match -i -r '^\s*Valid:.*'
        return 0
    end

    rm -f $cert_out
    echo "Failed to obtain workstation cert from $host" >&2
    return 1
end
