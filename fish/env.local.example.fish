# Copy to env.local.fish and fill in values. This file is safe to commit.
#   cp "$DOTFILES/fish/env.local.example.fish" "$DOTFILES/fish/env.local.fish"

set -gx MATURIN_PYPI_TOKEN ""
set -gx CLAUDE_CODE_OAUTH_TOKEN ""

# Workstation SSH target (clients). On the workstation itself, also set:
#   set -gx WORKSTATION_ROLE server
# set -gx WORKSTATION_SSH_HOST hduva
# set -gx WORKSTATION_SSH_USER hduva
# set -gx WORKSTATION_ROLE client
# set -gx ANTHROPIC_AUTH_TOKEN ""
# set -gx ANTHROPIC_BASE_URL https://api.example.com
# set -gx ANTHROPIC_DEFAULT_HAIKU_MODEL ""
# set -gx ANTHROPIC_DEFAULT_SONNET_MODEL ""
# set -gx ANTHROPIC_DEFAULT_OPUS_MODEL ""
# set -gx ANTHROPIC_MODEL ""
# set -gx CLAUDE_CODE_SUBAGENT_MODEL ""
# set -gx AWS_DEFAULT_PROFILE ""
