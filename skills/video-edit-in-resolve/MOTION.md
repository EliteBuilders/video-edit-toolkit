# Motion system

How graphics **move**, which **full-screen scenes** exist, how often they come, and the gate
they pass before anyone sees them. `SKILL.md` → *Motion graphics* owns what graphics *are*
(jobs, kit, colours, type, truth rules). This file owns how they behave. `BRAND.md` owns the
client's tokens; every colour below is the operator's house default and yields to it.

Read this at the start of phase 4, every run. Sound effects and the music bed live in
`AUDIO-PLAYBOOK.md` §6–7, because they are audio.

---

## 0. Who does what

**This skill runs the edit. HyperFrames' own skills are called to build a graphic, never to run
the job.** They were installed with `hyperframes skills` and several describe themselves as the
entry point for any video request. Inside a Resolve edit they are not: the cut, the gates, the
review and the render stay here.

| Need | Go to |
|---|---|
| Is there already a block or component for this? | `hyperframes-registry`, via `hyperframes catalog --query "<the move>" --json` |
| A motion recipe (count-up, path draw, camera push, keyword glow) | `hyperframes-animation` → `rules-index.md`, pick 2–4 rules |
| The composition contract (`data-*` timing, determinism) | `hyperframes-core` |
| A stand-alone graphic under ~10 s | `motion-graphics` |
| Sound effects, music, icons, logos, images | `media-use` (`resolve --type sfx|bgm|icon|logo|image`) |
| Worked, full compositions to study | `registry/examples/` in the HyperFrames clone, or `hyperframes init <dir> --example <name>` |

**Search the catalog before hand-building any named move.** 383 items, 160 blocks and 223
components at v0.8.68, searchable offline. Wiring a tested component and restyling it to
`BRAND.md` beats writing the same move from scratch, and it is where most of the polish in a
"designed" edit comes from. Restyle every item: a catalog default left as-is reads as a template.

```bash
HF="$(cat .hyperframes-path)/packages/cli/bin/hyperframes.mjs"
node "$HF" catalog --query "stat card count up" --json     # search by meaning or name
node "$HF" catalog --tag captions                           # browse a tag
node "$HF" add strikethrough-replace --dir <project>/graphics/hf --no-clipboard
```

The browsable versions are `hyperframes.heygen.com/catalog` and `/examples`; the local clone
holds the same items, so nothing needs a login.

---

## 1. The motion vocabulary

Numbers are at 30 fps. At 24 fps multiply by 0.8, at 60 fps by 2. These are **starting
defaults from standard motion practice, not measured on this operator's videos yet.** When the
operator corrects one, change the number here and date it (MAINTENANCE.md).

### Timing

| Move | Frames | Ease (GSAP) | Notes |
|---|---|---|---|
| Card or panel enters | 10–14 | `power3.out` | Decelerates into place. Arrivals slow down, never speed up |
| Text enters | 8–12 | `power2.out` + blur 8px→0 + y 16px→0 | `soft-blur-in` in the catalog |
| Chip, pill, check mark, badge | 8–10 | `back.out(1.6)` | **Overshoot is for small objects only.** Never on a headline or a panel |
| Row or item slides in | 10–12 | `expo.out` from 40–60 px off its lane | What makes a list feel fast without feeling rushed |
| Group stagger | 3–5 per item | — | Whole group ≤ 15 frames (0.5 s), or it stops reading as one beat |
| Exit | 6–9 | `power2.in` | **Exits are faster than entrances**, and quieter: fade plus 8–12 px drift, no bounce |
| Number count-up | 18–30 | `power2.out` | `tabular-nums` so the width never jitters |
| Line or path draws | 15–24 | `power2.inOut` | Endpoints pop *after* the line lands |

GSAP's `power2` is cubic, not quadratic (LEARNINGS, 2026-09-20). Pick eases by feel on a
preview, not by name.

### Sync to speech

- **An element lands on the frame its word is spoken.** Start the entrance so it *settles* on
  the word: `start = word_frame − entrance_frames + 2`. A list item that appears before its
  word is announced spoils it. One that appears after reads as late.
- **One new thing moves at a time.** If two elements animate together they are one element,
  or one of them waits.
- **Build, don't reveal.** A structure (a stack, a list, a flow) is on screen empty or as
  numbered slots first, then fills one item per spoken item. That is the promise-and-progress
  device the kit's list chips already use; full-screen scenes use it too.
- Every graphic exits at the next sentence boundary after its last element lands (SKILL.md,
  QA table). The gate checks it.

### Holds are never frozen

A full-screen scene held for more than ~2 s keeps one slow thing moving: a 1–3% push-in
across the hold, a playhead sweeping, a glow breathing at ≤ 0.45 opacity. HyperFrames rules:
`multi-phase-camera` (micro-drift), `ambient-glow-bloom`, `sine-wave-loop`. A dead-still frame
on a dark ground reads as a frozen render.

### Direction grammar

New information enters from the right or from below. Things that are finished leave up or to
the left. Keep it for the whole video: consistent direction is what makes a sequence feel
edited rather than assembled.

### Face ↔ full screen

**A full-screen scene cuts on and dissolves off** (LEARNINGS), timed to whole caption cues.
The cut happens on a word boundary. No whip or zoom transition into a full screen unless the
operator asks for one; the hard cut is the style.

### Optional: 12 fps stepped motion

Rendering the graphics layer's *motion* at 12 fps over 30 fps footage (catalog:
`stop-motion-cadence`) gives the choppy, hand-made look some creators use. It is a
whole-video decision, marked **TRY** in `EDIT-STYLE.md` until the operator adopts it. Never
mix stepped and smooth graphics in one video.

---

## 2. Full-screen dark scenes

The heaviest-lifting device in explainer edits: the talking head cuts away to a designed
full-frame scene that *shows* the idea being said. Each scene below does one of the jobs in
SKILL.md's reference loop. Build them in the operator's style (`BRAND.md`), never as a copy of
someone else's.

### The ground

- Radial ground from `#0F1626` at centre to `#070B14` at the edges, plus a soft vignette.
- Optional **grid**: 1 px lines at 4–6% white, 48–64 px cells, fading out toward the edges.
- Panels: fill `#0F1626` at 80–90%, 1 px border in the accent at 25–35%, **outer glow** in the
  accent at 20–40 px blur, 25–35% opacity. Corner radius 16–24 px.
- Scene title: small caps, letter-spaced, top centre, two tone: the key word in the accent
  tint (`#7BC8FF`), the rest white. It lands first, before anything else moves.

### The scenes

| Scene | Job | What it is | Catalog / rules to start from |
|---|---|---|---|
| **Stack build** | Name a structure | A panel with labelled rows; each row slides in from the right on its spoken word, a green check pops at its end, a playhead sweeps across the whole hold | `beat-timeline`, `stagger-cascade`, `success-check`, `state-chip-rail` |
| **Flow / node map** | Name a structure | A central node (orb or card) with labelled nodes wiring in by drawn lines, one per spoken item, then a result node | `constellation-hub`, `flowchart` block, rule `svg-path-draw`, `locked-nucleus-orbit` |
| **Document read-along** | Frame the screen / carry the words | The real text, static, full frame; spans highlight in the accent as the operator reads them | `inline-highlight`, `marker-highlight`, rule `asr-keyword-glow` |
| **Screen composite** | Frame the screen | A **real capture** (§3) in a window frame, a left column with small-caps kicker, bold title, italic-serif subline and one or two pills, and a hand-drawn arrow into the window; slow push-in | `browser-device-stage`, `device-frame-stage`, `ui-focus-zoom`, `hw-arrow` |
| **Statement** | Break the video up | One short line, two tone, centred. Once per section at most | `headline-slam`, `kinetic-center-build`, `titlecard-lockup` |
| **Proof** | Show proof | Number, chart or article with the claim highlighted | `count-up`, `number-pop-in`, `data-chart` block, `decline-chart`, SKILL.md proof highlight |

**Read-along rule:** the text itself never animates. Only the highlight moves. An animated
wall of text is the failure that ruined the one-shot edit's prompt scene.

### Overlays on the face, for contrast

Everything that is not a full screen is an overlay and follows the kit: a glass stat card
top-left (kicker, big value, one sub line; values change by `strikethrough-replace` or
count-up), list chips on the bottom strip, lower thirds bottom-left, viewfinder corner
brackets with a label for "this is the raw footage" moments. None of them may touch the face
zone or the caption zone; the gate measures both.

---

## 3. Real screen captures

**Anything the operator names that exists on a screen is shown as a real capture, never a
mockup.** A repo, a website, a community page, a project folder, an app. A drawn stand-in for
a real thing reads as fake, and the edit that used a generic graphic for a GitHub repo was
worse for it.

```bash
tools/window_grab.sh web https://github.com/<org>/<repo> graphics/cap/repo.png        # 1600x1000 @2x
tools/window_grab.sh web https://<site> graphics/cap/site-long.png 1600 4000        # tall, for a scroll
tools/window_grab.sh window "Finder" graphics/cap/folder.png                        # one window, no shadow
```

- Web: headless Chrome at 2x, so the still survives a push-in. A tall capture feeds a scroll
  move (rule `3d-page-scroll`).
- Window: the app must be open on screen. The terminal needs Screen Recording permission.
- **Look at every capture before it goes into a graphic.** No email, token, client name,
  notification or private tab. Crop rather than blur where you can.
- For moving captures (a click-through), record the screen and treat it as B-roll on an upper
  track; frame it in the screen-composite scene.

---

## 4. Phase 4, step by step

**4a. Plan.** Read the locked cut's transcript and write `graphics/graphics-plan.json`
(schema below) before building anything.

**Look it up in the operator's graphics library first** (the `video-edit-graphics-library` skill): for
every graphic in the plan, name its job, pick the library entry it borrows from, and write that
entry's id in the plan item's `ref`. System, never design; no entry more than ~4 times. Every cue anchored to a spoken word. Show the
operator the plan as a list, `time — scene or overlay — job — the words it carries`, and get a
yes. Plans are cheap to change; renders are not.

**Cadence, starting defaults** (long-form talking head; the brief overrides):

| Stretch | A visual change every | Full-screen share |
|---|---|---|
| Hook, first 30–60 s | 3–6 s | up to 50% when the operator asks to "lean on full screens" |
| Body | 8–15 s | 15–25% |
| A tutorial or demo stretch | on every named on-screen thing | as needed, real captures |

A visual change is a graphic, a full screen, a punch-in or a B-roll cut. Punch-ins stay native
in Resolve (SKILL.md). Record the operator's corrections to these numbers in `LEARNINGS.md`.

**4b. Build.** Catalog first (§0), then the rules, then the preview loop in SKILL.md: a live
HTML preview the operator can watch before any render. Render `--format mov` (ProRes 4444
alpha).

**4c. Gate.** Run the deterministic QA gate on the real render:

```bash
python3 tools/graphics_qa.py --plan graphics/graphics-plan.json \
        --render graphics/overlay.mov --round 1 --out graphics/qa-r1.json
```

Fix every FAIL, re-render, re-run with `--round 2`. **Three rounds, then stop**: anything still
failing goes to the operator as an open flag, with the report. The gate cannot judge taste, so
a pass is followed by the screenshot check in SKILL.md: every graphic, over its footage,
looked at.

**4d. Sound effects** from the plan, then **4e. music bed**, both per `AUDIO-PLAYBOOK.md`.
Re-run the gate after 4d: it checks every sound against a visible event.

---

## The graphics plan

One JSON file per video, `graphics/graphics-plan.json`. Frames are timeline frames at the
timeline's frame rate. The gate reads it; the SFX step writes into it.

```json
{
  "fps": 30, "width": 1920, "height": 1080,
  "render_offset": 0,
  "safe_margin": 0.05,
  "zones": {
    "face": [760, 120, 480, 560],
    "captions": [360, 860, 1200, 170]
  },
  "sentence_ends": [212, 431, 655],
  "caption_cues": [[0, 58], [58, 121]],
  "density": {"window_s": 30, "min_events": 3, "max_events": 10},
  "cues": [
    {
      "id": "stack-build", "kind": "fullscreen", "job": "name a structure",
      "start": 240, "end": 431, "words": 12,
      "events": [262, 298, 335, 371],
      "sfx": [{"frame": 262, "file": "assets/sfx/whoosh-soft.wav"}]
    },
    {
      "id": "hours-card", "kind": "overlay", "zone": "top-left", "job": "show proof",
      "start": 460, "end": 655, "words": 5, "events": [470, 540]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `kind` | `overlay`, `fullscreen` or `caption`. Full screens skip the face and zone checks |
| `zone` | Named screen area for overlays. Two overlays may not share one at the same time |
| `ref` | The video-edit-graphics-library entry id this treatment borrows from (4a), or `none` when it is original |
| `zones.face` | x, y, w, h of the speaker's head **with hair and hands at rest**, measured from a still of each camera setup. Look at the still; do not guess. A cue can override with its own `face` |
| `zones.captions` | Where captions live. Nothing but captions may enter it |
| `words` | Words a viewer must read on this graphic. Sets the minimum clean hold (3 words/s, 1 s floor) unless `min_hold` is given |
| `events` | Frames where something visibly lands. Sound effects may only sit on `start`, `end` or an event |
| `sentence_ends` | From the word-level transcript. Every non-caption graphic must exit on one |
| `caption_cues` | A full screen may not start or end in the middle of one |
| `render_offset` | Timeline frame at which the overlay render's frame 0 sits |
