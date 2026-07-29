set -gx PROJECTS "$HOME/projects"

set -gx DISABLE_NON_ESSENTIAL_MODEL_CALLS 1
set -gx DISABLE_TELEMETRY 1

set -gx POLARS_VERBOSE 1
set -gx RUST_BACKTRACE full
set -gx RUST_LOG warn
set -gx CARGO_PROFILE_RELEASE_BUILD_OVERRIDE_DEBUG true

if test "$_OS" = macos
    if test -d /Applications/Zed.app/Contents/MacOS
        fish_add_path /Applications/Zed.app/Contents/MacOS
    end
end

if test "$_OS" = linux
    if test -d /bin/stobe/Source
        set -gx STOBE /bin/stobe/
        set -gx STOBE_BASIS "$STOBE"Basis/
    end

    if test -d "$HOME/.jcmwave"
        set -gx JCMROOT "$HOME/.jcmwave/"
        set -gx JCMPYTHON "$JCMROOT"ThirdPartySupport/python/
        if set -q PYTHONPATH
            set -gx PYTHONPATH "$PYTHONPATH:$JCMPYTHON"
        else
            set -gx PYTHONPATH $JCMPYTHON
        end
    end
end

if test -r "$DOTFILES/fish/env.local.fish"
    source "$DOTFILES/fish/env.local.fish"
end
