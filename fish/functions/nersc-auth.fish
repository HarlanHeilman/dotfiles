function nersc-auth --description 'Refresh NERSC sshproxy cert (password + OTP required)'
    if not type -q sshproxy
        echo "sshproxy not found on PATH. Download it from https://portal.nersc.gov/cfs/mfa/ and install to ~/.local/bin/sshproxy"
        return 1
    end

    sshproxy -u hdh
end

function nersc-cert-status --description 'Show NERSC sshproxy cert validity'
    if not test -f ~/.ssh/nersc-cert.pub
        echo "No NERSC cert found at ~/.ssh/nersc-cert.pub. Run 'nersc-auth' first."
        return 1
    end

    ssh-keygen -L -f ~/.ssh/nersc-cert.pub | grep -i valid
end
