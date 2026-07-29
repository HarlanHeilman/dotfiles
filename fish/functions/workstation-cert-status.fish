function workstation-cert-status --description 'Show workstation SSH cert validity'
    set -l cert $HOME/.ssh/workstation-cert.pub
    if not test -f $cert
        echo "No workstation cert found at $cert. Run 'workstation-auth' first."
        return 1
    end
    ssh-keygen -L -f $cert | string match -i -r '^\s*Valid:.*'
end
