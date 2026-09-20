#!/bin/zsh
# Premaster -> delivered file.  Stage 3 of the pipeline; see PIPELINE.md.
#
#   ./deliver.sh <premaster.mov> <output.mp4> [speed]
#
# Speed defaults to 1.0 (no change). Pass 1.15 for a talking head that reads
# slow - anything past ~1.2 starts to sound processed.
#
# TARGETS ARE PROJECT-SPECIFIC. The ones below came from one client's VSL and
# are NOT defaults to copy blindly - read BRAND.md for the platform target
# (YouTube -14 LUFS / -1.0 dBTP is the common one) and set them here.
#
# Why these particular numbers, as a worked example of how to settle yours:
#   * loudnorm's own TP target is -3.0, not -1.0. At -1.0 the limiter could not
#     hold true peak afterwards; limit 0.80 still came back -0.2 dBTP
#   * the limiter runs at 0.72 for the same reason
#   * chasing I upward was NON-MONOTONIC - I=-13.0 came back quieter AND hotter
#     on peak than I=-13.8, so -13.8 it is
#   * EVERY variable in a filter string is braced. zsh eats `:l` in
#     `limit=$3:level=false` as a lowercase modifier, AND reads `$SPEED[v]` in
#     `setpts=PTS/$SPEED[v]` as an ARRAY SUBSCRIPT, which silently expands to
#     nothing and leaves ffmpeg parsing `PTS/`. Brace them all.
set -e

IN="$1"; OUT="$2"; SPEED="${3:-1.0}"
[[ -f "$IN" ]] || { echo "no premaster at $IN"; exit 1; }
TMP="$(dirname "$OUT")/.speed.mov"

# Stage 1 is the expensive one (a ~12GB ProRes intermediate). If it is already
# there and newer than the premaster, reuse it - a failure in stage 2 should not
# cost another 20 minutes of transcoding.
if [[ -f "$TMP" && "$TMP" -nt "$IN" ]]; then
echo "== 1/3  speed x$SPEED  (reusing $TMP)"
else
echo "== 1/3  speed x$SPEED"
ffmpeg -v error -y -i "$IN" \
  -filter_complex "[0:v]setpts=PTS/${SPEED}[v];[0:a]atempo=${SPEED}[a]" \
  -map "[v]" -map "[a]" -c:v prores_ks -profile:v 3 -c:a pcm_s24le -ar 48000 "$TMP"
fi

echo "== 2/3  loudness pass 1"
MEASFILE="$(dirname "$OUT")/.loudness.json"
if [[ -f "$MEASFILE" && "$MEASFILE" -nt "$TMP" ]]; then
MEAS=$(cat "$MEASFILE")
else
MEAS=$(ffmpeg -hide_banner -nostats -y -i "$TMP" \
  -af "loudnorm=I=-13.8:TP=-3.0:LRA=9:print_format=json" -f null - 2>&1 \
  | python3 -c "
import sys, json
s = sys.stdin.read()
if '{' not in s:
    sys.exit('loudnorm printed no JSON - it prints at INFO level, so do not run it with -v error')
print(json.dumps(json.loads(s[s.index('{'):s.rindex('}')+1])))")
echo "$MEAS" > "$MEASFILE"
fi
[[ -n "$MEAS" ]] || { echo 'loudness measurement failed'; exit 1; }
gi=$(echo $MEAS  | python3 -c "import sys,json;print(json.load(sys.stdin)['input_i'])")
gtp=$(echo $MEAS | python3 -c "import sys,json;print(json.load(sys.stdin)['input_tp'])")
glra=$(echo $MEAS| python3 -c "import sys,json;print(json.load(sys.stdin)['input_lra'])")
gth=$(echo $MEAS | python3 -c "import sys,json;print(json.load(sys.stdin)['input_thresh'])")
echo "   measured  I=$gi  TP=$gtp  LRA=$glra"

echo "== 3/3  loudness pass 2 + limiter + H.264"
LIMIT=0.72
ffmpeg -v error -y -i "$TMP" \
  -af "loudnorm=I=-13.8:TP=-3.0:LRA=9:measured_I=${gi}:measured_TP=${gtp}:measured_LRA=${glra}:measured_thresh=${gth}:linear=true,alimiter=limit=${LIMIT}:level=false" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 256k -ar 48000 "$OUT"

rm -f "$TMP"
echo "== verify"
ffmpeg -v error -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | tail -6
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
