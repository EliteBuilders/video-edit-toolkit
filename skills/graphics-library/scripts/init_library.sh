#!/usr/bin/env bash
# init_library.sh <path>   Create an empty graphics reference library at <path> (or adopt an
# existing one) and record where it lives for the skill. Idempotent: never overwrites an
# existing library.json, README or catalogued file.
set -euo pipefail
SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIB="${1:?usage: init_library.sh <path-to-library-folder>}"
LIB="$(mkdir -p "$LIB" && cd "$LIB" && pwd)"
python3 - "$SKILL/template/library.json" "$LIB" <<'PY'
import json, os, sys
tpl, lib = json.load(open(sys.argv[1])), sys.argv[2]
jp = os.path.join(lib, "library.json")
jobs = json.load(open(jp))["jobs"] if os.path.exists(jp) else tpl["jobs"]
for d in ["_inbox", "_tools"] + [j["folder"] for j in jobs]:
    os.makedirs(os.path.join(lib, d), exist_ok=True)
if not os.path.exists(jp):
    json.dump(tpl, open(jp, "w"), indent=1)
    print("  created library.json")
PY
[ -f "$LIB/README.md" ] || { cp "$SKILL/template/README.md" "$LIB/README.md"; echo "  created README.md"; }
cp "$SKILL/scripts/build.py" "$LIB/_tools/build.py"
printf '%s\n' "$LIB" > "$SKILL/.library-path"
python3 "$LIB/_tools/build.py" "$LIB"
echo "  library: $LIB  (recorded in $SKILL/.library-path, which git ignores)"
