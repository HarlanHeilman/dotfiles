function nersc-auth --description 'Compat wrapper: auth perlmutter'
    auth perlmutter $argv
end

function nersc-cert-status --description 'Compat wrapper: auth status perlmutter'
    auth status perlmutter $argv
end
