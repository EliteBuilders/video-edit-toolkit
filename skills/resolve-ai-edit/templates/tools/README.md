# Caption and graphics pipeline — the shape that works

Copy `build_srt.py` and `deliver.sh` into `<project>/tools/` on any new client,
set `EMPHASIS` from their `BRAND.md` and the loudness targets from their platform.
Everything below is the pattern they belong to, learned on a 24-ad batch and a
long-form VSL, and worth following from ad one.

**`../../PIPELINE.md` is the companion to this file** — it covers the three-stage
render pipeline these tools sit inside, and the variant/remap pattern.

## Why captions are generated, not set in Resolve

**Resolve's subtitle track exposes no styling to the API at all.** Colour, size,
stroke, position and any entrance animation are unreachable from scripting, so
anything beyond plain white text has to be built outside it.

The shape that works:

```
<ad>_cues.py       the cue table — the single source of truth for every word
<ad>_graphics.py   the graphics table, plus SKIP = cues a graphic takes over
<ad>_beats.py      the cut: src in/out, zoom, and framing offsets per beat
build_srt.py       cue table -> .srt sidecar, with the guards
build_overlay.py   cue table + graphics table -> an HTML/GSAP composition
deliver.sh         premaster -> speed -> loudness -> H.264 (stage 3)
```

The composition renders to a **ProRes 4444 alpha MOV on V2** over the footage on
V1. Because the SRT and the burn-in come from one table they cannot drift.

**The per-ad work is then the cut and the cue table.** That is the creative part
and it does not automate. Everything downstream of those two files is scripted.

## Three rules the guards enforce, and why each exists

1. **No caption block ends with a comma.** The block vanishes as a unit, so the
   comma punctuates nothing.
2. **No line is pinned within 12 frames of its cue's end.** A line pinned to its
   *last* word instead of its first showed for 4 frames and read as a flash.
3. **27 characters hard, 22 preferred, 2 lines maximum.** Beyond that it stops
   being readable at phone size.

## The one thing the guards do NOT cover

**Graphics.** There is no equivalent check on how long a finished graphic is
actually on screen before its exit begins. A payoff diagram that felt "held" was
clean for **8 frames** — a third of a second on the one frame the ad existed to
show. Count it in frames off a real render, every time.

## Timing rules that are not mechanical

- **Pin every line to the frame its FIRST word is spoken**, from word-level
  transcription. A fixed lag between lines puts words on screen before they are
  said, and the error is invisible until someone watches it.
- **Match what the speaker actually says.** Do not smooth their grammar.
- **Word-level transcription pads the end of a word.** The last beat should end
  where the mouth closes, not where the transcript's final word is timed.
