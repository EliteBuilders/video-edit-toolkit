#!/usr/bin/env bash
# link-skills.sh [--quiet]
#
# Symlinks every skill in skills/ into ~/.claude/skills/. Idempotent.
# Called by install.sh, and by this repo's own post-merge hook so that a
# `git pull` that adds a skill makes it invocable without anyone remembering to
# re-run the installer. Same model as elitebuilders-toolkit.
set -euo pipefail
TOOLKIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
QUIET=0; [ "${1:-}" = "--quiet" ] && QUIET=1
say(){ [ "$QUIET" -eq 1 ] || echo "$1"; }
mkdir -p "$SKILLS_DIR"

LINKED=0; CHANGED=0
for d in "$TOOLKIT"/skills/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  target="$SKILLS_DIR/$name"
  want="${d%/}"
  if [ -L "$target" ]; then
    [ "$(readlink "$target")" = "$want" ] && { LINKED=$((LINKED+1)); continue; }
    rm "$target"
  elif [ -e "$target" ]; then
    say "    !! $name exists and is NOT a symlink — backing up to $name.bak"
    mv "$target" "$target.bak"
  fi
  ln -s "$want" "$target"
  say "    linked $name"
  LINKED=$((LINKED+1)); CHANGED=$((CHANGED+1))
done

if [ "$CHANGED" -gt 0 ]; then
  say "    $LINKED skills linked ($CHANGED new or repointed)"
else
  say "    $LINKED skills already linked, nothing to do"
fi
