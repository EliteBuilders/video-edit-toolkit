#!/usr/bin/env python3
"""Measure an animation in a reference video, to the frame. 2026-09-25.

  motion_timing.py <video> <start-seconds> <duration-seconds> [--strip out.png] [--region x,y,w,h]

Prints the per-frame change (mean absolute luma difference to the previous
frame) across the window, then the MOTION BURSTS it finds: first and last frame,
duration in frames and seconds, and the shape of the curve (fast-in, fast-out,
even), which is what an ease looks like from outside. `--region` restricts the
measurement to where the graphic is, so a talking head moving behind it does not
count. `--strip` writes a contact sheet of every other frame for a visual check.

Why it exists: the video-vision MCP finds WHERE the animations are and shows
them, but its drill-in only takes whole-second timestamps. A 12-frame pop and a
30-frame slide look the same at one frame a second; this measures them.
"""
import subprocess, sys

args = [a for a in sys.argv[1:]]
src, ss, dur = args[0], float(args[1]), float(args[2])
strip = args[args.index("--strip") + 1] if "--strip" in args else None
region = args[args.index("--region") + 1] if "--region" in args else None
fps = float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=r_frame_rate", "-of", "csv=p=0", src],
                           capture_output=True, text=True).stdout.strip().split("/")[0] or 30)
fps = fps if fps < 200 else 30.0
if region:
    rx, ry, rw, rh = region.split(",")
    crop = "crop=%s:%s:%s:%s," % (rw, rh, rx, ry)        # ffmpeg order is w:h:x:y
else:
    crop = ""
out = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % ss, "-t", "%.3f" % dur, "-i", src,
                      "-vf", crop + "scale=320:-2,signalstats,metadata=print:key=lavfi.signalstats.YDIF:file=-",
                      "-f", "null", "-"], capture_output=True, text=True).stdout
d = [float(l.split("=")[1]) for l in out.splitlines() if "YDIF=" in l]
if not d:
    raise SystemExit("no frames read")
f0 = int(round(ss * fps))
print("per-frame change from frame %d (%.2fs), %.0f fps:" % (f0, ss, fps))
print(" ".join("%d:%.1f" % (f0 + i, v) for i, v in enumerate(d)))

# bursts: frames above a threshold relative to the window's quiet level
# the MEDIAN is the background (a talking head never stops moving); a graphic
# move stands clear of it. The quartile version merged a speaker's gestures
# into the card dissolve.
median = sorted(d)[len(d) // 2]
th = max(2.0, median * 2.5)
bursts, cur = [], None
for i, v in enumerate(d):
    if v > th:
        cur = [i, i] if cur is None else [cur[0], i]
    elif cur is not None and i - cur[1] > 2:          # allow 2 quiet frames inside one move
        bursts.append(cur); cur = None
if cur:
    bursts.append(cur)
print("\nmotion bursts (threshold %.1f):" % th)
for a, b in bursts:
    seg = d[a:b + 1]
    n = len(seg)
    peak = seg.index(max(seg))
    shape = ("fast-in, slow settle (ease-out)" if peak < n / 3 else
             "slow start, fast finish (ease-in)" if peak > 2 * n / 3 else "even / ease-in-out")
    if n <= 2:
        shape = "a cut (1-2 frames)"
    print("  frames %d-%d  %d frames = %.2fs  peak at +%d  %s" % (f0 + a, f0 + b, n, n / fps, peak, shape))

if strip:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % ss, "-t", "%.3f" % dur, "-i", src,
                    "-vf", "select='not(mod(n,2))',scale=240:-2,tile=8x%d" % max(1, (len(d) // 2 + 7) // 8),
                    "-frames:v", "1", strip], check=True)
    print("\nstrip:", strip, "(every other frame, left to right, top to bottom)")
