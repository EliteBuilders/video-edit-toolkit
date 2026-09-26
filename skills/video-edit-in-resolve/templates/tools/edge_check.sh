#!/bin/zsh
# Transcribe the first and last few seconds of every clip given: the proof that no
# cut clipped a word or left a stray one ("Yeah,", a trailing "I", a missing "course.").
# A caption list is not proof; the delivered audio is. 2026-09-25.
#   edge_check.sh [-s SECONDS] clip.mp4 [...]      (needs whisper-cli and a ggml model)
MODEL=${WHISPER_MODEL:-$HOME/.cache/hyperframes/whisper/models/ggml-medium.en.bin}
SEC=2.5
[[ "$1" == "-s" ]] && { SEC=$2; shift 2; }
TMP=$(mktemp -d)
for f in "$@"; do
  ffmpeg -v error -y -t $SEC -i "$f" -vn -ac 1 -ar 16000 "$TMP/h.wav"
  ffmpeg -v error -y -sseof -$SEC -i "$f" -vn -ac 1 -ar 16000 "$TMP/t.wav"
  H=$(whisper-cli -m "$MODEL" -f "$TMP/h.wav" -np -nt 2>/dev/null | tr -d '\n')
  T=$(whisper-cli -m "$MODEL" -f "$TMP/t.wav" -np -nt 2>/dev/null | tr -d '\n')
  print -r -- "${f:t} | HEAD:$H | TAIL:$T"
done
rm -rf "$TMP"
