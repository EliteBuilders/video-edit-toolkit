#!/usr/bin/env bash
# video-edit-toolkit installer. Run once after cloning. Re-runnable and idempotent.
set -euo pipefail
TOOLKIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> linking skills into $HOME/.claude/skills"
"$TOOLKIT/bin/link-skills.sh"

echo "==> installing auto-relink hooks"
for h in post-merge post-checkout; do
  if [ -f "$TOOLKIT/hooks/$h" ]; then
    install -m 0755 "$TOOLKIT/hooks/$h" "$TOOLKIT/.git/hooks/$h" 2>/dev/null \
      && echo "    installed $h" || echo "    !! could not install $h"
  fi
done

echo "==> machine setup"
echo "    Run ./bin/setup.sh once per machine — it installs the Resolve MCP server and"
echo "    HyperFrames, and checks ffmpeg. Skipped here because it clones and installs."

echo "==> checking prerequisites"
echo "    ?? DaVinci Resolve Studio 21.1+ must be running and reachable over MCP."
echo "       In Resolve: File > Setup AI Assistants. Free Resolve will not work —"
echo "       21.1 removed Python scripting from the free edition."
if command -v ffmpeg >/dev/null 2>&1; then
  echo "    ok  ffmpeg found (HyperFrames renders through it)"
else
  echo "    !!  no ffmpeg on PATH — HyperFrames cannot render graphics until it is installed"
fi

cat <<'MSG'

Done. Three skills:

    /video-edit-creative-brief   what should this brand look and feel like?   (once per brand)
    /video-edit-style             here is a reference — extract it and file it (whenever one arrives)
    /video-edit-in-resolve        cut it, grade it, graphic it                 (every video)

Start a project with:

    ./bin/new-project.sh <path-inside-the-client-folder>

No client lives in this repo. Read README.md for the folder layout, MAINTENANCE.md before
editing a skill, and DECISIONS.md before changing a rule.
MSG
