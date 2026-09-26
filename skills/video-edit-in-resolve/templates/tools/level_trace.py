#!/usr/bin/env python3
"""Per-frame loudness of a stretch of audio: where one word ends and the next begins.

  level_trace.py <audio-or-video> <start-seconds> <duration-seconds> [fps]

Prints `frame:dBFS` for every video frame (default 30fps), numbered from the
start of the file. Use it to place an edge the transcript cannot: a filler fused
into the next word ("Yeah, I think", "practice. So", "Um, I listened") has no
pause for a silence-snap to find, but it always has a dip between the words.
Cut at the dip, then prove the join with edge_check.sh. 2026-09-25.

Transcript word times are anchored loosely (up to 0.7s late on interviews, and
whisper on a short excerpt compresses timing); the level trace is the arbiter.
"""
import array, math, subprocess, sys

src, ss, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
fps = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0
rate = 48000
pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.4f" % ss, "-t", "%.4f" % dur, "-i", src,
                      "-vn", "-ac", "1", "-ar", str(rate), "-f", "s16le", "-"], capture_output=True).stdout
a = array.array("h", pcm)
n = int(rate / fps)
first = int(round(ss * fps))
out = []
for k, i in enumerate(range(0, len(a) - n + 1, n)):
    c = a[i:i + n]
    rms = math.sqrt(sum(x * x for x in c) / n) + 1e-9
    out.append("%d:%.0f" % (first + k, 20 * math.log10(rms / 32768)))
print(" ".join(out))
