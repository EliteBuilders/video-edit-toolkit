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

echo "==> 0/4  bun  (HyperFrames is a bun workspace — npm cannot resolve its deps)"
if command -v bun >/dev/null 2>&1; then
  say "ok" "bun $(bun --version 2>/dev/null)"
else
  say "MISS" "not found. Install with:  brew install oven-sh/bun/bun"
  say "-" "npm is not a substitute: HyperFrames packages depend on each other"
  say "-" "through \"workspace:^\", which npm cannot resolve at all."
  FAIL=1
fi

echo "==> 1/4  ffmpeg  (HyperFrames renders through it)"
if command -v ffmpeg >/dev/null 2>&1; then
  say "ok" "$(ffmpeg -version 2>/dev/null | head -1 | cut -c1-60)"
else
  say "MISS" "not found. Install with:  brew install ffmpeg"
  FAIL=1
fi

echo "==> 2/4  HyperFrames  (motion graphics as HTML/CSS, Apache 2.0, local, no API key)"
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
  # HyperFrames is a bun workspace: its packages depend on each other through
  # "workspace:^", which npm cannot resolve at all. bun or nothing.
  if [ -f "$HF_DIR/package.json" ] && [ ! -d "$HF_DIR/node_modules" ]; then
    if command -v bun >/dev/null 2>&1; then
      say "..." "installing dependencies with bun (first run only)"
      if ( cd "$HF_DIR" && bun install >/dev/null 2>&1 ); then
        say "ok" "dependencies installed"
      else
        say "MISS" "bun install failed. Run by hand:  cd $HF_DIR && bun install"
        FAIL=1
      fi
    else
      say "MISS" "bun not found — npm cannot resolve HyperFrames' workspace: deps."
      say "-" "install with:  brew install oven-sh/bun/bun"
      FAIL=1
    fi
  fi
  # The CLI ships unbuilt; without dist/ every render fails on a missing module.
  if [ -d "$HF_DIR/node_modules" ] && [ ! -f "$HF_DIR/packages/cli/dist/runtimeVersion.js" ]; then
    if command -v bun >/dev/null 2>&1; then
      say "..." "building packages (first run only, ~1 min)"
      ( cd "$HF_DIR" && bun run build >/dev/null 2>&1 ) \
        && say "ok" "build complete" \
        || { say "MISS" "build failed. Run by hand:  cd $HF_DIR && bun run build"; FAIL=1; }
    fi
  fi
  # Prove it actually runs. A present dist/ is not the same as a working CLI, and
  # trusting the build is what let the first version of this script report success
  # over a broken install.
  HF_CLI="$HF_DIR/packages/cli/bin/hyperframes.mjs"
  if [ -f "$HF_CLI" ]; then
    HF_VER="$(node "$HF_CLI" --version 2>/dev/null | head -1)"
    if [ -n "$HF_VER" ]; then
      say "ok" "CLI runs — hyperframes $HF_VER"
    else
      say "MISS" "CLI present but will not run. Try:  cd $HF_DIR && bun run build"
      FAIL=1
    fi
  else
    say "MISS" "CLI entry point missing at $HF_CLI"
    FAIL=1
  fi

  # Record where it landed so the skill does not have to guess.
  printf '%s\n' "$HF_DIR" > "$TOOLKIT/.hyperframes-path"
  say "ok" "path recorded in .hyperframes-path"
  say "-" "use the LOCAL CLI, not the hosted MCP — the hosted one needs a HeyGen account"
fi

echo "==> 3/4  DaVinci Resolve MCP"
if [ -d "/Applications/DaVinci Resolve" ]; then
  say "ok" "Resolve found in /Applications"
else
  say "WARN" "Resolve not in /Applications — install DaVinci Resolve STUDIO 21.1+ first"
fi
MCP_HOME="$HOME/Library/Application Support/davinci-resolve-mcp"
if [ -d "$MCP_HOME" ]; then
  say "ok" "MCP server already installed at $MCP_HOME"
elif [ -t 0 ]; then
  # The installer is interactive. Only run it when there is a terminal to answer it.
  say "..." "running: npx davinci-resolve-mcp setup   (interactive — answer its prompts)"
  if npx --yes davinci-resolve-mcp setup; then
    say "ok" "MCP setup completed"
  else
    say "MISS" "setup did not complete. Re-run by hand: npx davinci-resolve-mcp setup"
    FAIL=1
  fi
else
  say "MISS" "MCP server not installed, and this shell has no terminal to answer the"
  say "-"    "installer's prompts. Run this yourself:  npx davinci-resolve-mcp setup"
  FAIL=1
fi

echo "==> 4/4  Resolve settings you must set by hand"
say "-" "Preferences > General > 'External scripting using' = Local"
say "-" "  Without it the MCP connects but nothing can touch the timeline."
say "-" "File > Setup AI Assistants, then restart the agent."

cat <<'MSG'

  Studio, not free: 21.1 removed Python scripting from the free edition, so free
  Resolve cannot be driven at all. In Resolve: File > Setup AI Assistants, then
  restart the agent so it picks the server up.

MSG
[ "$FAIL" -eq 1 ] && { echo "  RESULT: incomplete — fix the MISS lines above"; exit 1; }
echo "  RESULT: ready"
