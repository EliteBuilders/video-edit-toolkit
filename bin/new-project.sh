#!/usr/bin/env bash
# new-project.sh <path>
#
# Scaffolds a video project that resolve-ai-edit and video-creative-brief can work in.
#
#   ./bin/new-project.sh ~/Video/resolve-agent
#   ./bin/new-project.sh ~/Video/clients/acme
#
# Idempotent. Files you have already edited are never overwritten — BRAND.md and
# BROLL.md are kept as-is if present, because they hold real brand decisions.
#
# Templates are read from skills/resolve-ai-edit/templates/, which is the versioned
# source. Ported from the josh-video-skills drop, which shipped its own stale copies.
set -euo pipefail

TOOLKIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TPL="$TOOLKIT/skills/resolve-ai-edit/templates"
PROJ="${1:-}"

if [ -z "$PROJ" ]; then
  echo "usage: $0 <project-path>" >&2
  echo "  e.g. $0 ~/Video/resolve-agent" >&2
  exit 2
fi
[ -d "$TPL" ] || { echo "!! templates not found at $TPL" >&2; exit 1; }

mkdir -p "$PROJ"/{raw,output,assets,reference,graphics/kit,broll/candidates}
echo "  dirs    raw output assets reference graphics/kit broll/candidates"

# Preserve anything already edited; these carry real decisions.
for f in BRAND.md BROLL.md; do
  if [ -f "$PROJ/$f" ]; then
    echo "  kept    $f (already edited)"
  else
    cp "$TPL/$f" "$PROJ/$f"; echo "  wrote   $f"
  fi
done

# These two are reference copies; safe to refresh so a toolkit update reaches the project.
for f in CREATIVE-BRIEF-TEMPLATE.md SPOT-BRIEF.md FIRST-RUN.md EDIT-STYLE.md; do
  cp "$TPL/$f" "$PROJ/$f"; echo "  wrote   $f"
done

# Media must never reach git. Raw footage will fill a repo in one shoot.
if [ -f "$PROJ/.gitignore" ]; then
  echo "  kept    .gitignore (already present)"
else
  cat > "$PROJ/.gitignore" <<'GI'
.DS_Store
*.mov
*.mp4
*.wav
*.aif
*.braw
*.r3d
raw/
output/
broll/candidates/
GI
  echo "  wrote   .gitignore"
fi

cat <<MSG

  Scaffolded $PROJ

  Next:
    1. Resolve:  File > Setup AI Assistants  (connect Claude Code, then restart it)
    2. cd "$PROJ" && claude
    3. Run the video-creative-brief skill to produce BRAND.md and CREATIVE-BRIEF.md
    4. Read FIRST-RUN.md before pointing resolve-ai-edit at footage you care about —
       the first run is meant to be a text-only cut list on a throwaway project.
MSG
