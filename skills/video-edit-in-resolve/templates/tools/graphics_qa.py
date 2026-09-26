#!/usr/bin/env python3
"""Graphics QA gate. Deterministic checks on a graphics plan and its real render.

    python3 graphics_qa.py --plan graphics-plan.json --render graphics/overlay.mov --round 1

Reads the plan (schema in MOTION.md, "The graphics plan"), reads the rendered overlay's
alpha channel frame by frame through ffmpeg, and fails on anything a reviewer would
catch: a graphic over the face, outside title safe, into the caption zone, on screen
too briefly to read, a full-screen card that half-covers a caption, an exit that
misses the sentence boundary, a sound effect with nothing visible under it.

Exit 0 = pass, 1 = fails to fix, 2 = round 4 or later (stop and hand to the operator).
Stdlib only, plus ffmpeg on PATH. Python 3.9+.
"""
import argparse
import json
import subprocess
import sys

MAX_ROUNDS = 3
SAMPLE_W, SAMPLE_H = 160, 90      # alpha is analysed at this size; plenty for boxes
ALPHA_ON = 16                     # alpha above this counts as painted
OVERLAP_TOL = 0.02                # >2% of a graphic's box inside a forbidden zone fails
HOLD_STABLE = 0.97                # "fully on" = opacity mass within 3% of the cue's peak
SFX_TOL = 2                       # frames either side of a visible event
EXIT_TOL = 4                      # frames after a sentence end an exit may start


def fail(out, cue, check, msg):
    out.append({"level": "FAIL", "cue": cue, "check": check, "msg": msg})


def warn(out, cue, check, msg):
    out.append({"level": "WARN", "cue": cue, "check": check, "msg": msg})


def box_area(b):
    return max(0, b[2]) * max(0, b[3])


def intersect(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    return [x1, y1, x2 - x1, y2 - y1] if x2 > x1 and y2 > y1 else [0, 0, 0, 0]


def union(a, b):
    if a is None:
        return b
    x1, y1 = min(a[0], b[0]), min(a[1], b[1])
    x2, y2 = max(a[0] + a[2], b[0] + b[2]), max(a[1] + a[3], b[1] + b[3])
    return [x1, y1, x2 - x1, y2 - y1]


def read_alpha(path, last_frame, want):
    """Return {frame: (opacity mass 0-1, bbox px-in-sample or None)} for frames in `want`.

    Mass is total alpha over the frame, so a card at 40% opacity weighs 40% of the same
    card fully on: the hold is measured on what is actually visible, not what is painted."""
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-frames:v", str(last_frame + 1),
           "-vf", "alphaextract,scale=%d:%d:flags=area" % (SAMPLE_W, SAMPLE_H),
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    table = bytes(0 if v < ALPHA_ON else 1 for v in range(256))
    size, zero, res, f = SAMPLE_W * SAMPLE_H, b"\x00", {}, 0
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        if f in want:
            mass = sum(buf) / (255.0 * size)
            buf = buf.translate(table)
            painted = size - buf.count(zero)
            bbox = None
            if painted:
                top = bottom = None
                left, right = SAMPLE_W, -1
                for r in range(SAMPLE_H):
                    row = buf[r * SAMPLE_W:(r + 1) * SAMPLE_W]
                    if row.count(zero) == SAMPLE_W:
                        continue
                    top = r if top is None else top
                    bottom = r
                    left = min(left, SAMPLE_W - len(row.lstrip(zero)))
                    right = max(right, len(row.rstrip(zero)) - 1)
                bbox = [left, top, right - left + 1, bottom - top + 1]
            res[f] = (mass, bbox)
        f += 1
    err = proc.stderr.read().decode(errors="replace").strip()
    proc.wait()
    if proc.returncode != 0 or (f == 0 and err):
        raise RuntimeError("ffmpeg could not read alpha from %s: %s" % (path, err[:300]))
    return res, f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--render", help="overlay render with alpha (ProRes 4444 MOV); omit for timing-only checks")
    ap.add_argument("--round", type=int, default=1, help="QA round; round %d is the last" % MAX_ROUNDS)
    ap.add_argument("--out", help="write the JSON report here")
    a = ap.parse_args()

    if a.round > MAX_ROUNDS:
        print("ROUND %d: the cap is %d. Stop rebuilding and hand the open fails to the operator." % (a.round, MAX_ROUNDS))
        sys.exit(2)

    plan = json.load(open(a.plan))
    fps = plan.get("fps", 30)
    W, H = plan.get("width", 1920), plan.get("height", 1080)
    margin = plan.get("safe_margin", 0.05)
    safe = [W * margin, H * margin, W * (1 - 2 * margin), H * (1 - 2 * margin)]
    zones = plan.get("zones", {})
    sentence_ends = sorted(plan.get("sentence_ends", []))
    caption_cues = plan.get("caption_cues", [])
    cues = plan["cues"]
    out = []

    # ---- timing checks: need only the plan -----------------------------------------
    for c in cues:
        cid, kind, s, e = c["id"], c.get("kind", "overlay"), c["start"], c["end"]
        if e <= s:
            fail(out, cid, "T1-duration", "end %d is not after start %d" % (e, s))
            continue
        if kind == "fullscreen":
            for cs, ce in caption_cues:
                for edge in (s, e):
                    if cs < edge < ce:
                        fail(out, cid, "T4-caption-cover",
                             "full-screen edge at %d cuts caption cue %d-%d; time it to whole cues" % (edge, cs, ce))
        if sentence_ends and kind != "caption":
            ok = any(se <= e <= se + EXIT_TOL for se in sentence_ends)
            if not ok:
                nxt = [se for se in sentence_ends if se >= e - EXIT_TOL]
                fail(out, cid, "T5-exit",
                     "exit at %d is not on a sentence end (next: %s)" % (e, nxt[0] if nxt else "none"))
        for sfx in c.get("sfx", []):
            fr = sfx["frame"]
            if kind == "caption":
                fail(out, cid, "S1-sfx", "sound on a caption cue at %d; captions are silent" % fr)
                continue
            visible = [s, e] + c.get("events", [])
            if not any(abs(fr - v) <= SFX_TOL for v in visible):
                fail(out, cid, "S1-sfx",
                     "sound at %d has no visible event within %d frames (events: %s)" % (fr, SFX_TOL, visible))

    # T3: two graphics in the same zone at the same time
    ov = [c for c in cues if c.get("kind", "overlay") == "overlay" and c.get("zone")]
    for i, x in enumerate(ov):
        for y in ov[i + 1:]:
            if x["zone"] == y["zone"] and x["start"] < y["end"] and y["start"] < x["end"]:
                fail(out, x["id"], "T3-zone", "shares zone '%s' with %s at the same time" % (x["zone"], y["id"]))

    # D1: density over sliding windows
    d = plan.get("density")
    if d:
        win = int(d.get("window_s", 60) * fps)
        starts = sorted(c["start"] for c in cues if c.get("kind") != "caption")
        span = max((c["end"] for c in cues), default=0)
        for w0 in range(0, max(1, span - win + 1), win // 2 or 1):
            n = sum(1 for s in starts if w0 <= s < w0 + win)
            if n < d.get("min_events", 0):
                warn(out, "-", "D1-density", "%d graphic events in %0.fs from %0.1fs (min %d)"
                     % (n, win / fps, w0 / fps, d["min_events"]))
            if n > d.get("max_events", 10 ** 9):
                warn(out, "-", "D1-density", "%d graphic events in %0.fs from %0.1fs (max %d)"
                     % (n, win / fps, w0 / fps, d["max_events"]))

    # ---- pixel checks: measured off the real render --------------------------------
    measured = {}
    if a.render:
        want, last = set(), 0
        for c in cues:
            off = c.get("render_offset", plan.get("render_offset", 0))
            want.update(range(c["start"] - off, c["end"] - off))
            last = max(last, c["end"] - off)
        try:
            alpha, nframes = read_alpha(a.render, last, want)
        except RuntimeError as ex:
            print("RENDER UNREADABLE: %s" % ex)
            sys.exit(1)
        sx, sy = W / SAMPLE_W, H / SAMPLE_H
        for c in cues:
            cid, kind = c["id"], c.get("kind", "overlay")
            off = c.get("render_offset", plan.get("render_offset", 0))
            frames = [f - off for f in range(c["start"], c["end"])]
            cov = [alpha.get(f, (0.0, None))[0] for f in frames]
            if c["end"] - off > nframes:
                fail(out, cid, "P0-length", "cue runs to render frame %d, render has %d frames" % (c["end"] - off, nframes))
            peak = max(cov) if cov else 0
            if peak < 0.001:
                fail(out, cid, "P4-missing", "nothing painted between %d and %d; check the render offset" % (c["start"], c["end"]))
                continue
            run = best = 0
            for v in cov:
                run = run + 1 if v >= peak * HOLD_STABLE else 0
                best = max(best, run)
            words = c.get("words", 0)
            need = c.get("min_hold", max(int(fps), int(words / 3.0 * fps)))
            measured[cid] = {"hold_frames": best, "peak_coverage": round(peak, 4)}
            if best < need:
                fail(out, cid, "T2-hold", "fully on screen for %d frames, needs %d (%d words)" % (best, need, words))
            if kind == "fullscreen":
                continue
            bb = None
            for f in frames:
                v, b = alpha.get(f, (0, None))
                if b and v >= peak * HOLD_STABLE:
                    bb = union(bb, [b[0] * sx, b[1] * sy, b[2] * sx, b[3] * sy])
            if not bb:
                continue
            measured[cid]["bbox"] = [round(v) for v in bb]
            area = box_area(bb)
            outside = area - box_area(intersect(bb, safe))
            if outside > area * OVERLAP_TOL:
                fail(out, cid, "P1-safe", "%.0f%% of the graphic is outside title safe" % (100 * outside / area))
            face = c.get("face", zones.get("face"))
            if face and box_area(intersect(bb, face)) > area * OVERLAP_TOL:
                fail(out, cid, "P2-face", "graphic box %s overlaps the face zone %s" % (measured[cid]["bbox"], face))
            cap = zones.get("captions")
            if kind != "caption" and cap and box_area(intersect(bb, cap)) > area * OVERLAP_TOL:
                fail(out, cid, "P3-caption-zone", "graphic box %s enters the caption zone %s" % (measured[cid]["bbox"], cap))
    else:
        warn(out, "-", "P-skipped", "no --render given: pixel checks and measured holds did not run")

    fails = [r for r in out if r["level"] == "FAIL"]
    print("GRAPHICS QA  round %d/%d  cues %d  fails %d  warnings %d"
          % (a.round, MAX_ROUNDS, len(cues), len(fails), len(out) - len(fails)))
    for r in out:
        print("  %-4s %-16s %-14s %s" % (r["level"], r["cue"], r["check"], r["msg"]))
    if not fails:
        print("  PASS. Now screenshot each graphic over its footage and look: this gate cannot judge taste.")
    elif a.round == MAX_ROUNDS:
        print("  Last round. Anything still failing goes to the operator as an open flag.")
    if a.out:
        json.dump({"round": a.round, "results": out, "measured": measured}, open(a.out, "w"), indent=2)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
