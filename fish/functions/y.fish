function y --description 'yazi that cd-s into the last directory on quit'
    set -l tmp (mktemp -t yazi-cwd.XXXXXX)
    command yazi $argv --cwd-file=$tmp
    if set -l cwd (cat -- $tmp); and test -n "$cwd"; and test "$cwd" != "$PWD"
        cd -- $cwd
    end
    rm -f -- $tmp
end
