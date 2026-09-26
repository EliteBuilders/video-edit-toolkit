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

echo "==> 2b/4 HyperFrames agent skills + reference tools"
if [ -f "${HF_CLI:-}" ]; then
  if [ -d "$HOME/.claude/skills/hyperframes-registry" ]; then
    say "ok" "HyperFrames skills installed (catalog, animation rules, media-use)"
  else
    # Installs for Claude Code and Codex. video-edit-in-resolve stays the entry point; see MOTION.md §0.
    node "$HF_CLI" skills </dev/null >/dev/null 2>&1 \
      && say "ok" "HyperFrames skills installed for Claude Code and Codex" \
      || say "WARN" "skills install failed. Run by hand:  node $HF_CLI skills"
  fi
fi
command -v yt-dlp >/dev/null 2>&1 \
  && say "ok" "yt-dlp (pulls reference videos for frame study)" \
  || say "WARN" "yt-dlp not found (optional, for reference study):  brew install yt-dlp"

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

echo "==> 3b/4 Video vision  (watch reference videos; local-only, pinned)"
# claude-video-vision (MIT, github.com/jordanrendric/claude-video-vision): frame extraction +
# transcription over MCP, so a reference VIDEO or YouTube link can be read for its graphics.
# PINNED: its own plugin manifest runs `npx claude-video-vision@latest`, so every start would
# run whatever was last published, unreviewed. 1.3.2 was audited 2026-09-25 (execFile only,
# two deps, no install scripts; network = whisper model download, yt-dlp, opt-in cloud APIs).
# LOCAL backend: nothing leaves the machine. Change VV_VERSION only after reading the diff.
VV_VERSION="1.3.2"
if ! command -v claude >/dev/null 2>&1; then
  say "-" "claude CLI not found; skipped (optional)"
elif claude mcp list 2>/dev/null | grep -q "claude-video-vision@${VV_VERSION}"; then
  say "ok" "claude-video-vision@${VV_VERSION} already registered"
else
  claude mcp remove -s user claude-video-vision >/dev/null 2>&1 || true
  claude mcp add -s user claude-video-vision -- npx -y "claude-video-vision@${VV_VERSION}" >/dev/null \
    && say "ok" "registered claude-video-vision@${VV_VERSION} (user scope)" \
    || say "MISS" "could not register; run: claude mcp add -s user claude-video-vision -- npx -y claude-video-vision@${VV_VERSION}"
fi
if command -v codex >/dev/null 2>&1; then
  if codex mcp get claude-video-vision 2>/dev/null | grep -q "claude-video-vision@${VV_VERSION}"; then
    say "ok" "Codex: claude-video-vision@${VV_VERSION} already registered"
  else
    codex mcp remove claude-video-vision >/dev/null 2>&1 || true
    codex mcp add claude-video-vision -- npx -y "claude-video-vision@${VV_VERSION}" >/dev/null \
      && say "ok" "Codex: registered claude-video-vision@${VV_VERSION}" \
      || say "MISS" "Codex: run  codex mcp add claude-video-vision -- npx -y claude-video-vision@${VV_VERSION}"
    # a cold npx start fetches the package; Codex's default startup wait is shorter
    python3 - "$HOME/.codex/config.toml" <<'PY' || true
import sys
p = sys.argv[1]; s = open(p).read()
hdr = "[mcp_servers.claude-video-vision]"
if hdr in s and "startup_timeout_sec" not in s.split(hdr, 1)[1].split("\n[", 1)[0]:
    head, tail = s.split(hdr, 1)
    body, rest = (tail.split("\n[", 1) + [""])[:2]
    s = head + hdr + body.rstrip("\n") + "\nstartup_timeout_sec = 120\n" + ("\n[" + rest if rest else "")
    open(p, "w").write(s)
PY
  fi
else
  say "-" "codex CLI not found; skipped Codex registration (optional)"
fi
VVCFG="$HOME/.claude-video-vision/config.json"
if [ ! -f "$VVCFG" ]; then
  mkdir -p "$HOME/.claude-video-vision/models"
  printf '{\n  "backend": "local",\n  "whisper_engine": "cpp",\n  "whisper_model": "medium.en",\n  "frame_resolution": 768\n}\n' > "$VVCFG"
  say "ok" "local backend configured ($VVCFG)"
else
  say "ok" "config exists, left alone ($VVCFG)"
fi
command -v whisper-cli >/dev/null 2>&1 || say "-" "brew install whisper-cpp   (local transcription)"
command -v yt-dlp >/dev/null 2>&1 || say "-" "brew install yt-dlp        (YouTube links)"

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
