# Custom agent skills

Put one folder per skill here (`my-skill/SKILL.md`). `install.py` links each into
`~/.agents/skills/`, the shared directory used by Claude Code and opencode, and
links everything in `~/.agents/skills/` into `~/.claude/skills/`.

Skills installed from elsewhere (`hf-cli`, `find-skills`) stay where their installers
put them and are only linked, so their own update commands keep working.
