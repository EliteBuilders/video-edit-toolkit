# VSL playbook

A long-form sales video is the most expensive thing in this toolkit to get wrong, because every
correction costs a render. The first one shipped after **12 end-to-end renders and 18 review
rounds**. Almost none of that was necessary.

**The whole point of this file: settle everything that can be settled on a STILL, a TEXT FILE or
in the TIMELINE, before a single frame is rendered.** Everything below follows from that.

---

## What actually cost the time

Honest accounting from the first VSL, worst first:

| Cost | Why | Now prevented by |
|---|---|---|
| **Audio, 5 rounds** | Wrong tool (expander, not Voice Isolation), then boosting into a limiter, then unasked-for changes to an approved region | `AUDIO-PLAYBOOK.md`, and step 5 below |
| **Centring, 3 rounds** | Measured the frame, not the face. A detector locked onto a chair back and a bookshelf and reported "centred" while his nose sat 120px off | Step 2: ruler on a still, read the nose |
| **Captions, 3 rounds** | Rules discovered one at a time in review instead of asserted in the generator | Step 3: the generator asserts all of them |
| **Graphics duration, 2 rounds** | Exits hand-picked instead of derived from speech | Step 4: exit at the next sentence |
| **Several full re-renders** | Audio-only changes triggered video re-renders | Step 6: audio never needs a video render |

**None of these were creative disagreements.** Every one was a mechanical thing that could have
been checked before rendering. The operator's taste notes — testimonial placement, photo choice,
the proof-first variant — were fast and cheap. Assume that is always the split, and spend your
care on the mechanical half.

---

## The order

### 1. Cut as text, and speed-check it
Beat table in code. Get the runtime target **before** cutting — dropping explanation to shorten a
video is the operator's call, not a default. Detect retakes by diffing transcripts; never trust
"Part 2/3/4" to mean sequence.

A talking head that reads slow can take **1.15×**. Past ~1.2 it sounds processed.

### 2. Framing, settled on stills — never on a render
For every distinct setup, export one still and **draw a ruler on it** with `drawbox`. Read the
subject's **nose**, not a bounding box; a detector will find furniture and lie to you.

Then respect the geometry, which is not negotiable:

```
max |tilt| = (frame_height / 2) * (zoom - 1)
```

Exceed it and the frame edge shows as a black bar exactly as tall as the overshoot. If the
subject must move further, **zoom more — never raise the tilt**. At full tilt, a feature `y` px
down the source lands at `y * zoom`, which tells you before rendering whether a head clears a
title bar.

Scale alternation on hard cuts: **scale pan and tilt by the same ratio** or the centring undoes
itself every other beat.

### 3. Captions, settled as a printed cue list
Print the cues and read them. The generator must assert, not hope:

- no cue spans a cut
- none under 3 words
- none ends on a dangling function word
- none opens with the previous sentence's last word
- no internal sentence boundary **after any pass that moves words between cues**
- no trailing comma or period on a block
- word durations clamped (~1s) so a swallowed pause cannot hide
- the last cue on a segment runs to its cut
- adjacent cues butt together and hand over in ~2 frames

One generator feeds both the burn-in and the `.srt`. Two generators drift.

### 4. Graphics, timed from speech
Every cue anchored to the frame a word is spoken. **Every graphic exits at the next sentence
boundary** after its last element lands — derived, never guessed, and only ever shortening a
hand-set end. Check each graphic outlasts its own build.

### 5. Audio, settled in the timeline before any render
See `AUDIO-PLAYBOOK.md`. The three that cost rounds:

- **Echo → Voice Isolation** (~85), never an expander or gate
- **Level → trim to the operator's timeline**, never boost into a limiter
- **Balance every speaker region** to within ~1 LU of the others; programme loudness on target
  means nothing if the host is 12 dB under the inserts

**Set the level where the operator can hear it.** They can; you cannot.

### 6. Render — and know what a render actually is
Three programs, not one (`PIPELINE.md`). The consequence that saves the most time:

> **An audio change NEVER needs a video re-render.** Render audio only (~1 min), mux with
> `-c:v copy`, and prove the picture is untouched with `-f md5` on the video stream.

That one move turned a 45-minute cycle into 2 minutes, repeatedly, at the end of this project.

### 7. Variants are an ORDER, not a second cut
One canonical `SEGMENTS`; a variant permutes it and `remap()` carries every measured cue to the
same moment. Select with an env var so both versions build from identical source.

If the permutation only reshuffles segments among themselves, everything after the permuted block
lands on identical frames — so a proof-first cut and a proof-late cut can share a bit-identical
close, and the only variable in an A/B is the structure. **Loudness-match the variants** or the
louder one wins for a reason that is not the edit.

---

## Review loop

Send **one sheet per round**, not one file per question:

- a contact sheet of the moments that changed
- the numbers: duration, LUFS, true peak, LRA, **crest**
- each open decision as a numbered question with a recommendation

And **say which pipeline stage you are in, by number**. "Rendering" means nothing to an operator
looking at three Resolve jobs sitting at 100%. They will ask whether it "downloaded"; the only
honest signal is the deliverable's modified time.

## Housekeeping

Premasters are ~13 GB each. This project left **60 GB** of scratch. Delete all but the premaster
behind the approved cut, once approved.
