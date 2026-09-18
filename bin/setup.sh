#!/usr/bin/env bash
# video-edit-toolkit one-time machine setup.
#   ./bin/setup.sh [--hyperframes-dir <path>]
# Installs the two things the skills drive: the Resolve MCP server and the
# HyperFrames renderer. Idempotent — safe to re-run, never overwrites a clone.
set -uo pipefail
TOOLKIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HF_DIR="${HYPERFRAMES_DIR:-$HOME/Tools/hyperframes}"
[ "${1:-}" = "--hyperframes-dir" ] && HF_DIR="$2"

say()  { printf '  %-6s %s\n' "$1" "$2"; }
FAIL=0

echo "==> 1/3  ffmpeg  (HyperFrames renders through it)"
if command -v ffmpeg >/dev/null 2>&1; then
  say "ok" "$(ffmpeg -version 2>/dev/null | head -1 | cut -c1-60)"
else
  say "MISS" "not found. Install with:  brew install ffmpeg"
  FAIL=1
fi

echo "==> 2/3  HyperFrames  (motion graphics as HTML/CSS, Apache 2.0, local, no API key)"
if [ -d "$HF_DIR/.git" ]; then
  say "ok" "already cloned at $HF_DIR"
else
  mkdir -p "$(dirname "$HF_DIR")"
  if git clone --quiet https://github.com/heygen-com/hyperframes.git "$HF_DIR" 2>/dev/null; then
    say "ok" "cloned to $HF_DIR"
  else
    say "MISS" "clone failed. Check network, then: git clone https://github.com/heygen-com/hyperframes.git $HF_DIR"
    FAIL=1
  fi
fi
if [ -d "$HF_DIR" ]; then
  if [ -f "$HF_DIR/package.json" ] && [ ! -d "$HF_DIR/node_modules" ]; then
    say "..." "installing dependencies (first run only)"
    ( cd "$HF_DIR" && npm install --silent >/dev/null 2>&1 ) \
      && say "ok" "dependencies installed" \
      || say "WARN" "npm install failed — run it by hand in $HF_DIR"
  fi
  # Record where it landed so the skill does not have to guess.
  printf '%s\n' "$HF_DIR" > "$TOOLKIT/.hyperframes-path"
  say "ok" "path recorded in .hyperframes-path"
  say "-" "use the LOCAL CLI, not the hosted MCP — the hosted one needs a HeyGen account"
fi

echo "==> 3/3  DaVinci Resolve MCP"
if [ -d "/Applications/DaVinci Resolve" ]; then
  say "ok" "Resolve found in /Applications"
else
  say "WARN" "Resolve not in /Applications — install DaVinci Resolve STUDIO 21.1+ first"
fi
say "..." "running: npx davinci-resolve-mcp setup"
if npx --yes davinci-resolve-mcp setup; then
  say "ok" "MCP setup completed"
else
  say "MISS" "setup did not complete. Re-run by hand: npx davinci-resolve-mcp setup"
  FAIL=1
fi

cat <<'MSG'

  Studio, not free: 21.1 removed Python scripting from the free edition, so free
  Resolve cannot be driven at all. In Resolve: File > Setup AI Assistants, then
  restart the agent so it picks the server up.

MSG
[ "$FAIL" -eq 1 ] && { echo "  RESULT: incomplete — fix the MISS lines above"; exit 1; }
echo "  RESULT: ready"
