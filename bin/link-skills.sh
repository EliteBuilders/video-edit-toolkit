#!/usr/bin/env bash
# link-skills.sh [--quiet]
#
# Symlinks every skill in skills/ into ~/.claude/skills/ (Claude Code), and
# ~/.codex/skills/ and ~/.agents/skills/ (Codex). Idempotent.
# Called by install.sh, and by this repo's own post-merge hook so that a
# `git pull` that adds a skill makes it invocable without anyone remembering to
# re-run the installer. Same model as local-seo-client-delivery.
set -euo pipefail
TOOLKIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# ~/.codex/skills is where the Codex app and CLI list skills; ~/.agents/skills is the
# cross-agent location. Link into both so every skill here works in Codex as in Claude Code.
SKILLS_DIRS=("$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.codex/skills")

# Only the main checkout owns the links. The hooks fire in every `git worktree`
# too, and a scratch worktree once silently repointed the live skills at itself,
# so a session mid-edit read a branch copy missing its own unsaved notes.
GIT_DIR="$(git -C "$TOOLKIT" rev-parse --absolute-git-dir 2>/dev/null || true)"
COMMON_DIR="$(cd "$TOOLKIT" && cd "$(git rev-parse --git-common-dir 2>/dev/null || echo .)" && pwd)"
if [ -n "$GIT_DIR" ] && [ "$GIT_DIR" != "$COMMON_DIR" ]; then
  [ "${1:-}" = "--quiet" ] || echo "    worktree checkout: skills stay linked to the main checkout"
  exit 0
fi
QUIET=0; [ "${1:-}" = "--quiet" ] && QUIET=1
say(){ [ "$QUIET" -eq 1 ] || echo "$1"; }

LINKED=0; CHANGED=0
for SKILLS_DIR in "${SKILLS_DIRS[@]}"; do
  mkdir -p "$SKILLS_DIR"
  for d in "$TOOLKIT"/skills/*/; do
    [ -d "$d" ] || continue
    name="$(basename "$d")"
    target="$SKILLS_DIR/$name"
    want="${d%/}"
    if [ -L "$target" ]; then
      [ "$(readlink "$target")" = "$want" ] && { LINKED=$((LINKED+1)); continue; }
      rm "$target"
    elif [ -e "$target" ]; then
      say "    !! $target exists and is NOT a symlink — backing up to $name.bak"
      mv "$target" "$target.bak"
    fi
    ln -s "$want" "$target"
    say "    linked $name -> $SKILLS_DIR"
    LINKED=$((LINKED+1)); CHANGED=$((CHANGED+1))
  done
done

if [ "$CHANGED" -gt 0 ]; then
  say "    $LINKED skills linked ($CHANGED new or repointed)"
else
  say "    $LINKED skills already linked, nothing to do"
fi
