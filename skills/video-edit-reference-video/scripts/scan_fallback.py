#!/usr/bin/env python3
"""Find the graphic moments in a reference video without the MCP. 2026-09-25.

  scan_fallback.py <video-file-or-URL> [--out DIR] [--threshold 2.0] [--start S] [--end S]

The same first pass the video-vision MCP gives (scene changes), for when that
server is not connected. A URL is downloaded with yt-dlp (<= 1080p). Scene
changes closer than 0.6s are merged into one moment. Writes, into DIR:
  moments.json   [{"n": 1, "t": 12.4}, ...]
  NN_<t>.jpg     one frame 0.3s after each change (the graphic settled)
  sheet.jpg      all of them, numbered left to right, top to bottom
Then time the ones the operator picks with motion_timing.py.
"""
import json, os, re, subprocess, sys, tempfile

args = sys.argv[1:]
if not args:
    raise SystemExit(__doc__)
src = args[0]
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
out = os.path.abspath(opt("--out", tempfile.mkdtemp(prefix="refscan-")))
th = float(opt("--threshold", "2.0"))     # scdet score, 0-100 (same scale the MCP reports)
os.makedirs(out, exist_ok=True)

if re.match(r"https?://", src):
    tpl = os.path.join(out, "source.%(ext)s")
    subprocess.run(["yt-dlp", "-q", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b", "--merge-output-format",
                    "mp4", "-o", tpl, src], check=True)
    src = next(os.path.join(out, f) for f in os.listdir(out) if f.startswith("source."))

trim = []
if "--start" in args:
    trim += ["-ss", opt("--start", "0")]
if "--end" in args:
    trim += ["-to", opt("--end", "0")]
err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + trim + ["-i", src, "-an", "-vf",
                      "scale=320:-2,scdet=threshold=%s" % th, "-f", "null", "-"],
                     capture_output=True, text=True).stderr
base = float(opt("--start", "0"))
# scdet logs "lavfi.scd.time: 12.4" per change. Its select-filter cousin only
# fires on hard cuts and missed every overlay and dissolve in a test render.
ts = [base + float(t) for t in re.findall(r"lavfi\.scd\.time:\s*([\d.]+)", err)]
moments = []
for t in ts:
    if not moments or t - moments[-1] > 0.6:
        moments.append(t)
rows = []
for n, t in enumerate(moments, 1):
    f = os.path.join(out, "%02d_%.1f.jpg" % (n, t))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % (t + 0.3), "-i", src, "-frames:v", "1",
                    "-vf", "scale=480:-2", f])
    rows.append({"n": n, "t": round(t, 2), "frame": os.path.basename(f)})
json.dump({"source": src, "moments": rows}, open(os.path.join(out, "moments.json"), "w"), indent=1)
frames = [os.path.join(out, r["frame"]) for r in rows if os.path.exists(os.path.join(out, r["frame"]))]
if frames:
    cols = 5
    lst = os.path.join(out, "frames.txt")
    open(lst, "w").write("".join("file '%s'\n" % f for f in frames))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf",
                    "scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2,"
                    "tile=%dx%d" % (cols, (len(frames) + cols - 1) // cols), "-frames:v", "1",
                    os.path.join(out, "sheet.jpg")])
print("%d moments in %s" % (len(rows), src))
for r in rows:
    print("  %2d  %6.2fs" % (r["n"], r["t"]))
print("out:", out)
