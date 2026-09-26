# The render pipeline, and the project tools that drive it

`SKILL.md` says *what* to do at each stage. This file says *how the machine is actually wired* —
the thing you cannot infer from the API docs and will otherwise rediscover over a long afternoon.

Read it before your first render. It is short.

---

## 1. Three programs, not one

The single most confusing thing about this system, and the first question a real operator asked:

> *"I'm seeing three rendered videos in DaVinci so I was just trying to check because I'm not
> sure if they are done and then it just downloads to the folder or not."*

**DaVinci's render queue never shows you a finished video.** Every job in it produces an
intermediate. The file a human watches is made by a third program, minutes later.

```
  ┌──────────────┐   transparent ProRes 4444    ┌──────────────┐
  │ HyperFrames  │ ───────────────────────────► │              │
  │ HTML+GSAP    │   overlay-*.mov  (~4 GB)     │   DaVinci    │   ProRes 422 HQ
  │ captions +   │                              │   Resolve    │ ─────────────────┐
  │ graphics     │                              │  V1 footage  │  *-premaster.mov │
  └──────────────┘                              │  V2 overlay  │     (~12 GB)     │
                                                └──────────────┘                  │
                                                                                  ▼
                    the file people watch    ┌──────────┐    speed change,  ┌──────────┐
                  ◄────────────────────────  │  ffmpeg  │ ◄─────────────────│ scratch  │
                        ~320 MB .mp4         │ deliver  │  loudness, H.264  │  folder  │
                                             └──────────┘                   └──────────┘
```

| Stage | Tool | Output | Where | Time |
|---|---|---|---|---|
| 1 | HyperFrames | `overlay-*.mov`, alpha | project `graphics/` | **8–25 min** |
| 2 | Resolve | `*-premaster.mov` | **scratch temp dir** | ~25 s |
| 3 | ffmpeg | the deliverable `.mp4` | project `output/` | **20–30 min** |

**Consequences worth internalising:**

- A **"Complete" job in Resolve means stage 2 finished.** Nothing watchable exists yet.
- Premasters are ProRes at ~25 MB/s. Five of them is **47 GB**. They go in a scratch directory,
  never the client folder, and get cleaned once a cut is approved.
- **Nothing uploads or downloads.** Every byte is local. If someone asks "has it downloaded yet",
  the honest answer is that no transfer exists anywhere in this pipeline.
- The deliverable is **overwritten in place** under one stable filename, so there is never a
  choice of files. **The way to tell whether a render landed is the deliverable's modified
  time**, not the Resolve queue.

Tell the operator which stage you are in, with a number. "Rendering" means nothing to someone
watching three jobs sit at 100%.

---

## 2. The per-project `tools/` module layout

Anything measured belongs in code that diffs, never in a chat message or a one-off command. A
mature project ends up with these, and they compose in one direction:

```
<project>/tools/
  <p>_beats.py        SEGMENTS: the cut, as data. Framing per beat. ORDER for variants
  <p>_captions.py     word timings -> cue list. Every grouping rule lives here
  <p>_graphics.py     GRAPHICS: each overlay cue, anchored to a spoken word
  build_<p>_overlay.py  the three above -> one HTML/GSAP composition for HyperFrames
  build_<p>_srt.py    the SAME cue list -> sidecar .srt, speed-corrected
  build_lut.py        measured white balance -> baked .cube
  deliver.sh          premaster -> speed -> loudness -> H.264
```

**The dependency order is strict and one-way:** `beats` → `captions` → `graphics` → `overlay`.
Captions import the cut; graphics import both; the overlay builder imports everything. Nothing
imports the overlay builder. Break this and you get an import cycle that is miserable to unpick.

### Why the cut is data

`SEGMENTS` is a list of `(source, in, out, note)`. Everything downstream derives from it:

- Word timings map onto the timeline through it, so **fixing a cut re-times every caption for
  free**
- Graphics are declared at the frame a word is spoken, so a cut change moves them correctly
- The `.srt` comes from the same cue list as the burned captions, so they can never disagree

One generator per artefact. **Two generators for one set of captions is a bug waiting to
happen** — they drift, and nobody notices until a viewer turns CC on and reads something
different from what is on screen.

### Variants are an ORDER, not a second table

When a client wants "the same video but with the testimonials at the front", do **not** copy the
beat table. Keep one canonical `SEGMENTS` and permute it:

```python
ORDER = None                      # None = natural
def order_testimonials_first():
    rest = [i for i in natural_order() if i not in TESTIMONIAL_IDX]
    return TESTIMONIAL_IDX + rest

def remap(f):
    """A frame in the NATURAL timeline -> the same moment in the current one."""
```

Every graphic cue was measured against the natural cut; `remap()` carries each one to the same
*moment* under any ordering. Re-measuring per variant is exactly how two versions of one video
drift apart. Select the ordering with an env var so both versions build from identical source
with nothing edited between them:

```
VSL_ORDER=testimonials-first python3 build_vsl_overlay.py
```

**Bonus property worth checking for:** if the permutation only reshuffles segments among
themselves, the total length is unchanged and every segment after the permuted block lands at an
identical frame — so the close, the CTA and the end card are bit-identical across variants.

### Re-cuts are declared, not re-typed

When a segment changes length, every hand-measured graphic frame after it moves. Declare the
edit once and apply it:

```python
CUT_DELTAS = [
  (5190,  16),   # extended so the last word is not clipped
  (15514, -12),  # trimmed a phantom word and dead air
]
def shift(f):
    return f + sum(d for at, d in CUT_DELTAS if f >= at)
```

Re-typing forty measured frames is how one of them gets mistyped.

---

## 3. Verification loops, cheapest first

Never ship on intention. Each of these costs seconds and has caught a real defect:

| Question | Check |
|---|---|
| Is the subject centred? | Export a still, draw a ruler with `drawbox`, read the nose position |
| Does a transition actually cover the cut? | `alphaextract` the overlay at the cut frame, count opaque pixels |
| Is there a black bar? | Crop the top 8 rows, measure mean/min luma. A bar is uniformly ~0 |
| Did the speed change apply? | `ffprobe` duration on the intermediate, compare to premaster ÷ speed |
| Is the grade neutral? | Whole-frame white point (see below) |
| Is loudness right? | `ebur128=peak=true`, read the Summary block |

### Measuring a colour cast

Average every pixel with `min(r,g,b) ≥ 140` and `max−min ≤ 30` — that is the set of bright,
near-neutral pixels, and their mean is the white point. Report `R−G` and `B−G`.

**Do not hand-pick patches.** That is the failure mode this method exists to prevent; picking by
eye was wrong three times in a row on one shoot (a shirt, a title, a blue graphic). If a clip has
too few qualifying pixels, take the correction from a sibling clip of the same setup and verify
by eye — do not lower the threshold until something passes, because what passes will be the
subject's clothing.

### Geometry that bites

Pan and tilt are **output pixels about frame centre**, and the zoom bounds how far they can go:

```
max |tilt| = (frame_height / 2) * (zoom - 1)
```

Exceed it and you expose the frame edge as a black bar — the overshoot in pixels *is* the bar's
height. If a subject needs to move further than the zoom allows, **zoom more**; do not increase
the tilt. And when a scale change is part of the look, scale pan and tilt by the same ratio or
the centring undoes itself on every other beat.

At maximum tilt the top of the source sits on the top of the frame, so a feature `y` pixels down
the source lands at `y * zoom`. That one line tells you, before rendering, whether a head will
clear a title bar.

---

## 4. Costs to budget for

- **A full-frame CSS `filter: blur()` is re-rasterized on every captured frame.** It made one
  overlay render 3× slower. Bake dim/blur/saturation into the source image with ffmpeg instead —
  identical result, no per-frame cost.
- Animating `scale` on a large `<img>` is the next most expensive thing. Worth it for a few
  hundred frames, not for thousands.
- A HyperFrames capture parallelises across ~5 Chrome workers into per-worker directories and
  merges at the end. **Counting files in `captured-frames/` reads zero until it finishes** — look
  in `capture-attempt-0/worker-*/` for real progress.

---

## 5. Where everything else lives

| You want | File |
|---|---|
| The stages, the gates, the QA checklists | `SKILL.md` |
| Resolve API behaviour that contradicts the docs | `RESOLVE-API-TRAPS.md` |
| Craft rules earned from operator corrections | `LEARNINGS.md` |
| A caption generator with the guards already in it | `templates/tools/build_srt.py` |
| A delivery script with the shell traps already fixed | `templates/tools/deliver.sh` |

**Two shell traps that cost real time, both zsh:**

```zsh
setpts=PTS/$SPEED[v]            # $SPEED[v] parses as an ARRAY SUBSCRIPT -> empty
limit=$LIMIT:level=false        # $LIMIT:l  parses as the LOWERCASE MODIFIER -> eats the option
```

Brace every variable inside an ffmpeg filter string. Both failures surface *after* the expensive
stage has already run, which is why the delivery template caches its measurements and makes each
stage resumable.

And: **`loudnorm` prints its JSON at INFO level.** Running the measurement pass with `-v error`
swallows it silently and the parse dies on a missing `{`.
