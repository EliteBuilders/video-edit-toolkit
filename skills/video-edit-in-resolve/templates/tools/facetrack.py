#!/usr/bin/env python3
"""Where the speaker's face is, over time: the horizontal path a 4:5 crop follows.

  facetrack.py <source> <crop-width> <x-min> <x-max> [--cmd FILE]
      -> JSON {"path": [[t, x], ...]} on stdout; with --cmd, also an ffmpeg sendcmd file
         that sets a crop named "tr" every 1/60s:
         -vf "sendcmd=f=FILE,crop@tr=W:H:X0:0,..."

Operator, 2026-09-25, on 4:5 reframes of webcam testimonials: "he's moving around so we need to keep his
head centered on the screen" and "since he's moving we probably
need to do a little bit of face tracking". A crop that follows every
twitch reads as a shaky camera, so the path is heavily smoothed: a detection
every 0.2s, gaps filled, a 1.4s median, then a 2.4s average, sampled every 0.5s.
Needs OpenCV 4.x: `pip install "opencv-python-headless<5"`. OpenCV 5 removed
CascadeClassifier. Drive the crop with ffmpeg `sendcmd` from the path, not an
expression: crop's parser fails past ~40 piecewise terms.
"""
import json, sys
import cv2
import numpy as np

src, cw, xmin, xmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])  # --cmd FILE optional
cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
nfr = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
step = max(1, int(round(fps * 0.2)))
ts, xs = [], []
last = None
for i in range(0, nfr, step):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, fr = cap.read()
    if not ok:
        break
    sc = 480.0 / fr.shape[1]
    g = cv2.cvtColor(cv2.resize(fr, None, fx=sc, fy=sc), cv2.COLOR_BGR2GRAY)
    faces = casc.detectMultiScale(g, 1.1, 5, minSize=(40, 40))
    cx = None
    if len(faces):
        # the biggest face, or the one nearest the last if two are close in size
        faces = sorted(faces, key=lambda f: -f[2] * f[3])
        f = faces[0]
        if last is not None and len(faces) > 1 and faces[1][2] > 0.8 * f[2]:
            f = min(faces[:2], key=lambda f: abs((f[0] + f[2] / 2) / sc - last))
        cx = (f[0] + f[2] / 2) / sc
        last = cx
    ts.append(i / fps)
    xs.append(cx)
xs = np.array([np.nan if v is None else v for v in xs], float)
ok = ~np.isnan(xs)
if ok.sum() < 3:
    raise SystemExit("facetrack: no face found in %s" % src)
xs = np.interp(np.arange(len(xs)), np.flatnonzero(ok), xs[ok])
med = np.array([np.median(xs[max(0, k - 3):k + 4]) for k in range(len(xs))])
k = 12
sm = np.convolve(np.pad(med, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
out, t = [], 0.0
while t <= ts[-1] + 1e-6:
    x = float(np.interp(t, ts, sm)) - cw / 2
    out.append([round(t, 3), int(round(min(max(x, xmin), xmax - cw)))])
    t += 0.5
if "--cmd" in sys.argv:
    lines, t = [], 0.0
    while t <= out[-1][0]:
        k = min(int(t / 0.5), len(out) - 2)
        (t0, x0), (t1, x1) = out[k], out[k + 1]
        lines.append("%.4f crop@tr x %d;" % (t, round(x0 + (x1 - x0) * min(1, max(0, (t - t0) / (t1 - t0))))))
        t += 1 / 60.0
    open(sys.argv[sys.argv.index("--cmd") + 1], "w").write("\n".join(lines) + "\n")
print(json.dumps({"width": W, "found": int(ok.sum()), "samples": len(ok), "path": out}))
