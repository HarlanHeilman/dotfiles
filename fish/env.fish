set -gx PROJECTS "$HOME/projects"

if not set -q WORKSTATION_SSH_HOST; or test -z "$WORKSTATION_SSH_HOST"
    set -gx WORKSTATION_SSH_HOST hduva
end
if not set -q WORKSTATION_SSH_USER; or test -z "$WORKSTATION_SSH_USER"
    set -gx WORKSTATION_SSH_USER hduva
end

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

    if test -d "$HOME/.jcm"
        set -gx JCMROOT "$HOME/.jcm"
    end
end

if test -r "$DOTFILES/fish/env.local.fish"
    source "$DOTFILES/fish/env.local.fish"
end
