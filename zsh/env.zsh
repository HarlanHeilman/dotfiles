export PROJECTS="${PROJECTS:-$HOME/projects}"

export DISABLE_NON_ESSENTIAL_MODEL_CALLS=1
export DISABLE_TELEMETRY=1

export POLARS_VERBOSE=1
export RUST_BACKTRACE="full"
export RUST_LOG="warn"
export CARGO_PROFILE_RELEASE_BUILD_OVERRIDE_DEBUG=true

if [[ "$_OS" == "linux" ]]; then
    if [[ -d "/bin/stobe/Source" ]]; then
        export STOBE="/bin/stobe/"
        export STOBE_BASIS="${STOBE}Basis/"
    fi

    if [[ -d "$HOME/.jcmwave" ]]; then
        export JCMROOT="$HOME/.jcmwave/"
        export JCMPYTHON="${JCMROOT}ThirdPartySupport/python/"
        export PYTHONPATH="${PYTHONPATH}:${JCMPYTHON}"
    fi
fi

[[ -r "$DOTFILES/zsh/env.local.zsh" ]] && source "$DOTFILES/zsh/env.local.zsh"
