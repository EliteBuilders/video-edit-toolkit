#!/usr/bin/env bash
# Real screen captures for graphics. Never a mockup of something that exists.
#
#   window_grab.sh web    <url> <out.png> [width] [height]   # headless Chrome, 2x, clean
#   window_grab.sh window "<App Name>" <out.png>              # one app window, no shadow
#   window_grab.sh list                                        # on-screen windows and their ids
#
# web:    fixed viewport (default 1600x1000) at device scale 2, scrollbars hidden. Pass a
#         tall height (e.g. 4000) to get a long page for a scroll move.
# window: captures the app's frontmost on-screen window by id, so the result does not
#         depend on what else is open. The app must be open and not minimised.
#
# Afterwards LOOK at the PNG before it goes near a graphic: no email, token, client name,
# notification or private tab in frame. SKILL.md's screen-recording rule applies to stills.
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

windows() {
  # Prints "id<TAB>app<TAB>title" for every normal on-screen window.
  /usr/bin/swift - <<'SWIFT' 2>/dev/null
import CoreGraphics
let opts = CGWindowListOption(arrayLiteral: .optionOnScreenOnly, .excludeDesktopElements)
for w in (CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]]) ?? [] {
  guard (w[kCGWindowLayer as String] as? Int) == 0 else { continue }
  let id = w[kCGWindowNumber as String] as? Int ?? 0
  let app = w[kCGWindowOwnerName as String] as? String ?? ""
  let title = w[kCGWindowName as String] as? String ?? ""
  print("\(id)\t\(app)\t\(title)")
}
SWIFT
}

case "${1:-}" in
  web)
    url="${2:?url}"; out="${3:?out.png}"; w="${4:-1600}"; h="${5:-1000}"
    [ -x "$CHROME" ] || { echo "Google Chrome not found at $CHROME" >&2; exit 1; }
    "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
      --window-size="$w,$h" --virtual-time-budget=8000 --screenshot="$out" "$url" >/dev/null 2>&1
    [ -s "$out" ] || { echo "capture failed: $url" >&2; exit 1; }
    echo "$out  ($(sips -g pixelWidth -g pixelHeight "$out" | awk '/pixel/{printf "%s ", $2}'))"
    ;;
  window)
    app="${2:?App Name}"; out="${3:?out.png}"
    id="$(windows | awk -F'\t' -v a="$app" '$2==a {print $1; exit}')"
    if [ -z "$id" ]; then
      echo "no on-screen window for '$app'. Open windows:" >&2; windows | cut -f2 | sort -u >&2
      echo "If the list is empty, grant Screen Recording to your terminal in System Settings." >&2
      exit 1
    fi
    screencapture -x -o -l "$id" "$out"
    echo "$out  (window $id of $app)"
    ;;
  list) windows ;;
  *) sed -n '2,15p' "$0"; exit 1 ;;
esac
