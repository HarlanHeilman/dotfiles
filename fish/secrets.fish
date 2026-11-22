# Names of env vars whose values live in the macOS login Keychain (service "dotfiles:NAME").
# Values are never stored in this repo. Add one:  secret set NAME   then list it below.
set -g __keychain_secrets MATURIN_PYPI_TOKEN CLAUDE_CODE_OAUTH_TOKEN ALS_TOKEN SUPABASE_ACCESS_TOKEN

for __name in $__keychain_secrets
    set -l __value (security find-generic-password -a $USER -s "dotfiles:$__name" -w 2>/dev/null)
    test -n "$__value"; and set -gx $__name $__value
end
set -e __name
